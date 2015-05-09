$(function ()
{
    var anchor = $(location).attr('hash').replace('#', '');
    var graph_timer;
    var cycle_timer;

    var black_or_white = function (color)
    {
        var rgb = color.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
        return (0.2126 * rgb[1] + 0.7152 * rgb[2] + 0.0722 * rgb[3]) < 150 ? 'black' : 'white';
    };

    var clear_legend = function (plot, opts)
    {
        $('#legend_elems').text('');
    };

    var format_legend = function (label, series)
    {
        $('#legend_elems').append(
            $('<div/>',
            {
                class: 'width-100 label label-' + black_or_white(series.color),
                css: {'background-color': series.color},
                id: 'legend_elems_'+label,
                text: label
            })
        );
    };

    var plot;
    var plot_data = {
        crosshair: {
            mode: 'x'
        },
        grid: {
            hoverable: true,
            clickable: true
        },
        hooks: {
            processOffset: [clear_legend]
        },
        legend: {
            show: true,
            container: $('#legend_phony'),
            sorted: true,
            labelFormatter: format_legend
        },
        series: {
            shadowSize: 0,
            lines: {show: true}
        },
        xaxis: {
            mode: 'time',
            timeformat: '%d.%m - %H:%M',
            timezone: 'browser',
            tickFormatter: function (value, axis)
            {
                return time_fmt(value);
            },
            panRange: [0.1, null],
            zoomRange: [0.1, null]
        },
        yaxis: {
            zoomRange: false,
            panRange: false
        },
        yaxes: [
            {}, // 1: numbers
            {
                tickFormatter: function (value, axis)
                {
                    return byte_fmt(value);
                }
            }, // 2: bytes
            {
                mode: "time",
                timezone: "browser",
                tickFormatter: function (value, axis)
                {
                    return uptime_fmt(value);
                }
            } // 3: seconds
        ]
    };

    function run_graph()
    {
        function draw_graph(collection)
        {
            function draw_callback(data)
            {
                $('#plot').removeClass('hide');
                $('#legend').removeClass('hide');

                $('#plot').on('plotclick plothover', function (event, pos, item)
                {
                    if (pos !== undefined && pos !== null)
                    {
                        $.each(plot.getData(), function (i, dset)
                        {
                            var ptime = null;
                            var label = null;
                            var last = $(dset.data.filter(function(idx){ return idx[0] <= pos.x; })).first()[0];
                            if (last !== undefined && last !== null)
                            {
                                ptime = time_fmt(pos.x);
                                switch (dset.yaxis.n)
                                {
                                    case 1: label = last[1] + ' [' + last[1] + ']'; break;
                                    case 2: label = byte_fmt(last[1]) + ' [' + last[1] + ']'; break;
                                    case 3: label = uptime_fmt(last[1]) + ' [' + last[1] + ']'; break;
                                    default: break;
                                }
                                if (label !== undefined && label !== null)
                                {
                                    $('#legend_elems_'+dset.label).text(dset.label + ' (' + label + ' - ' + ptime + ')');
                                }
                            }
                        });
                    }
                });
                plot = $.plot('#plot', data, plot_data);

                function move_around (dim, ax)
                {
                    clearInterval(graph_timer);
                    clearInterval(cycle_timer);
                    (dim ?
                        (ax ? plot.zoom() : plot.zoomOut())
                    :
                        plot.pan({left: (ax ? 60 : -60)})
                    );
                }

                function render_navigation (icon, dim, ax)
                {
                    return $('<li/>').append(
                        $('<a/>',
                        {
                            class: 'fa ' + icon
                        })
                    ).on('click', function (cl)
                    {
                        move_around(dim, ax);
                    });
                }

                $('#navigation_elems').html(
                    render_navigation('fa-chevron-left', false, false)
                ).append(
                    render_navigation('fa-minus', true, false)
                ).append(
                    render_navigation('fa-plus', true, true)
                ).append(
                    render_navigation('fa-chevron-right', false, true)
                );
                $('#navigation').removeClass('hide');

                $(document).on('keypress', function(ke)
                {
                    console.log('ke.key');
                    console.log(ke.key);
                    switch (ke.key)
                    {
                        case 'h': move_around(false, false); break;
                        case 'j': move_around(true, false); break;
                        case 'k': move_around(true, true); break;
                        case 'l': move_around(false, true); break;
                        case 'r': draw_graph(collection); break;
                        default: break;
                    }
                });
            }

            $(document).off('keypress');

            $('#source_elems_'+collection).parent().siblings().each(function (i, se)
            {
                $(se).removeClass('active');
            });
            $('#source_elems_'+collection).parent().addClass('active');

            clearInterval(graph_timer);
            graph_timer = setInterval(function() {
                draw_graph(collection);
            }, refresh_seconds());

            api_query('graph/'+collection, draw_callback);
        }

        function graph_callback(collections)
        {

            $('#source_elems').text('');
            $('#sources').removeClass('hide');

            var draw_num = 0;

            $.each(collections, function (i, collection)
            {
                $('#source_elems').append(
                    $('<li/>',
                    {
                        id: collection
                    }).append(
                        $('<a/>',
                        {
                            id: 'source_elems_'+collection,
                            text: collection
                        }).on('click', function (cl)
                        {
                            clearInterval(cycle_timer);
                            draw_graph(collection);
                        })
                    )
                );

                if (anchor.indexOf(collection) === 0 || i == draw_num)
                {
                    draw_graph(collection);
                }
            });

            if(anchor.indexOf('cycle') === 0)
            {
                clearInterval(cycle_timer);
                cycle_timer = setInterval(function() {
                    clearInterval(graph_timer);
                    draw_num = (draw_num + 1 < collections.length ? draw_num + 1 : 0);
                    draw_graph(collections[draw_num]);
                }, 2 * refresh_seconds());
            }
        }

        api_query('graph', graph_callback);
    }

    run_graph();

});
