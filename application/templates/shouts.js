$(function ()
{
    var shout_timer;
    var wdh = 3;

    function run_shouts()
    {
        function shouts_callback(shouts)
        {
            $('#{{ the_shouts }}').text('');
            $('#{{ the_shouts }}').removeClass('hide');

            $.each(shouts, function (i, shout)
            {
                var elem = (i - (i % wdh));
                var block = (
                    (i % wdh) !== 0 ? $('#block_'+elem) : $('<div/>',
                    {
                        id: 'block_'+elem,
                        class: 'units-row end'
                    })
                ).append(
                    $('<div/>',
                    {
                        class: 'unit-33',
                        id: '{{ the_shouts }}_' + shout.time
                    }).append(
                        $('<i/>',
                        {
                            class: 'left fa ' + shout.value.match(/fa-\S+/)
                        })
                    ).append(
                        $('<blockquote/>',
                        {
                            class: 'end',
                            style: 'word-wrap: break-word;',
                            text: shout.value.replace(/\s*fa-\S+/g, '.')
                        })
                    ).append(
                        $('<cite/>',
                        {
                            id: 'toggle_'+i,
                            class: 'small left',
                            text: reltime_fmt(shout.time)
                        })
                    )
                );

                $('#{{ the_shouts }}').append(block);
            });
        }

        api_query('data/{{ the_shouts }}', shouts_callback);
        clearInterval(shout_timer);
        shout_timer = setInterval(function() {
            run_shouts();
        }, refresh_seconds());
    }

    run_shouts();

    $('#shout').on('keyup focusin', function()
    {
        len = $('#shout').val().length;
        if (len < 5 || len > 142)
        {
            $('#counter').removeClass('fa-hand-o-right').addClass('fa-strikethrough');
        } else
        {
            $('#counter').removeClass('fa-strikethrough').addClass('fa-hand-o-right');
        }
        $('#counter').text(' ' + (len < 10 ? '0' + len: len));
    });
    $('#shout').on('focusout', function()
    {
        $('#counter').removeClass('fa-strikethrough').addClass('fa-hand-o-right').text('');
    });

});
