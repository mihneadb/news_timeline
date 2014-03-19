var storyTemplate = Handlebars.compile($('#story-template').html());

function stripHTML(text) {
    return $("<div/>").html(text).text();
}

function renderStory(story) {
    story.summary = stripHTML(story.summary);
    story.photos = story.photos.slice(0, 9);

    story.sentiment.positive = (story.sentiment.positive / story.sentiment.total * 100) | 0;
    story.sentiment.negative = (story.sentiment.negative / story.sentiment.total * 100) | 0;
    story.sentiment.neutral = (story.sentiment.neutral / story.sentiment.total * 100) | 0;

    var $rendered = $(storyTemplate(story));
    $('.container').append($rendered);

    var $photos = $rendered.find('.photos');
    $photos.imagesLoaded(function () {
        $photos.masonry({
            columnWidth: 256,
            itemSelector: 'img',
            isFitWidth: true,
            gutter: 1
        });
    });
}

$.getJSON("data.json")
    .done(function (data) {
        data.map(renderStory);
    });
