$(function ()
{
    var anchor = $(location).attr('hash').replace('#', '');

    function render_table()
    {
        return $('<table/>',
        {
            class: 'table-hovered table-flat'
        });
    }

    function render_table_keyval(key, val, varval, thkey, errorval)
    {
        return $('<tr/>').append(
            $('<'+(thkey ? 'th' : 'td')+'/>',
            {
                class: 'width-50',
                text: key
            })
        ).append(
            $('<td/>',
            {
                class: 'width-50 text-centered',
            }).append(
                $('<'+(varval ? 'var' : 'span')+'/>',
                {
                    class: (errorval ? 'error' : ''),
                    text: val
                })
            )
        );
    }

    function render_table_elemdata(dt, hidden, fmt_func, del_func)
    {
        var $value = $('<var/>',
        {
            text: dt.value
        });
        var $trash = $('<span/>',
        {
            class: 'right error hide'
        }).on('click', function (cl)
        {
            del_func(cl, $value);
        });

        return $('<tr/>',
        {
            class: (hidden ? 'hide' : '')
        }).on('click', function (cl)
        {
            $trash.removeClass('hide').addClass('fa fa-trash-o');
        }).append(
            $('<td/>',
            {
                class: 'width-25',
                text: time_fmt(dt.time)
            })
        ).append(
            $('<td/>',
            {
                class: 'width-25 text-centered',
                text: reltime_fmt(dt.time)
            })
        ).append(
            $('<td/>',
            {
                class: 'width-25 text-centered',
            }).append(
                $('<var/>',
                {
                    text: fmt_func(dt.value)
                })
            )
        ).append(
            $('<td/>',
            {
                class: 'width-25 text-centered',
            }).append(
                $value
            ).append(
                $trash
            )
        );
    }

    function draw_unit(unit)
    {
        $('#units').removeClass('hide');
        var $result = render_table().append(
            render_table_keyval(unit.name, unit.description, false, true)
        ).append(
            render_table_keyval('axis', unit.axis, true)
        ).append(
            render_table_keyval('sensors', unit.sensors.length, true)
        );

        $.each(unit.sensors, function (i, sn)
        {
            $result.append(
                render_table_keyval(null, sn)
            );
        });

        $('#unit_elems_'+unit.name).html($result);
    }

    function draw_sensor(sensor)
    {
        function data_callback(data)
        {
            var wdh = 25;
            var fmt_func;
            switch (sensor.unit_axis)
            {
                case 2: fmt_func = byte_fmt; break;
                case 3: fmt_func = uptime_fmt; break;
                default: fmt_func = function (x){}; break;
            }
            var $result = render_table();

            $.each(data, function (i, dt)
            {
                $result.append(
                    render_table_elemdata(dt, (i >= wdh), fmt_func, function (cl, rfield)
                    {
                        api_query('data/'+sensor.name, function ()
                        {
                            api_query('data/'+sensor.name, data_callback);
                        }, 'DELETE', dt, function (ex, err, eex) {
                            rfield.addClass('error').text(err + ' - ' + eex);
                        });
                    })
                );
            });

            $('#'+sensor.collection+'_'+sensor.name).html(
                $('<div/>',
                {
                    class: 'group width-100'
                }).append(
                    $result
                ).append(
                    $('<code/>',
                    {
                        id: sensor.collection+'_'+sensor.name+'_count',
                        class: 'right',
                        text: (wdh >= data.length ? data.length : wdh) + '/' + data.length
                    })
                )
            );

            if (data.length > wdh)
            {
                var dsp = wdh;
                $('#'+sensor.collection+'_'+sensor.name).append(
                    $('<div/>',
                    {
                        id: sensor.collection+'_'+sensor.name+'_load',
                        class: 'group text-centered'
                    }).append(
                        $('<button/>', {
                            class: 'btn fa fa-chevron-down'
                        }).on('click', function (cl)
                        {
                            dsp += wdh;
                            $.each($result.find('tr').slice(0, dsp), function (i, rs)
                            {
                                $(rs).fadeIn('slow');
                            });
                            $('#'+sensor.collection+'_'+sensor.name+'_count').text((dsp >= data.length ? data.length : dsp) + '/' + data.length);
                            if (dsp >= data.length)
                            {
                                $('#'+sensor.collection+'_'+sensor.name+'_load').addClass('hide');
                            }
                        })
                    )
                );
            }
        }

        $('#sensors').removeClass('hide');
        var latest = {
            outdated: false,
            value: null,
            reltime: null,
            result: 0
        };
        if (sensor.data_latest !== undefined && sensor.data_fresh !== undefined)
        {
            latest.outdated = !sensor.data_fresh;
            latest.value = sensor.data_latest.value;
            latest.reltime = reltime_fmt(sensor.data_latest.time);
            res = sensor.data_latest.value*sensor.factor;
            latest.result = (res ?
                res.toFixed(1)
            : 0);
        }
        $('#sensor_elems_'+sensor.name).html(
            $('<h2/>',
            {
                class: 'text-centered',
                text: sensor.name
            })
        ).append(
            $('<div/>',
            {
                id: 'data_'+sensor.name
            }).append(
                $('<' + (latest.outdated ? 'del' : 'span') + '/>',
                {
                    class: 'big'
                }).append(
                    $('<a/>',
                    {
                        class: 'accordion-title',
                        href: '#'+sensor.collection+'_'+sensor.name,
                        text: latest.result + '%'
                    })
                )
            ).append(
                $('<div/>',
                {
                    class: 'accordion-panel end',
                    id: sensor.collection+'_'+sensor.name
                }).append(
                    $('<div/>',
                    {
                        class: 'group text-centered'
                    }).append(
                        $('<i/>',
                        {
                            class: 'fa fa-circle-o-notch fa-spin'
                        })
                    )
                )
            )
        ).append(
            render_table().append(
                render_table_keyval(sensor.name, sensor.description, false, true)
            ).append(
                render_table_keyval('data', sensor.data_len, true)
            ).append(
                render_table_keyval('factor', sensor.factor, true)
            ).append(
                render_table_keyval(latest.reltime, latest.value, true, false, latest.outdated)
            ).append(
                render_table_keyval('unit', sensor.unit)
            )
        );

        $('#data_'+sensor.name).accordion({
            scroll: false,
            collapse: true,
            toggle: true
        }).on('opened.tools.accordion', function(title, panel)
        {
            api_query('data/'+sensor.name, data_callback);
        });

    }

    function draw_collection(collection)
    {
        function collection_callback(collection)
        {
            $('#collections').removeClass('hide');
            $('#sensor_elems').html('');

            $('#collection_descr').html(
                render_table().append(
                    render_table_keyval(collection.name, collection.description, false, true)
                    ).append(
                        render_table_keyval('sensors', collection.sensors.length, true)
                    )
            );

            $.each(collection.sensors, function (i, sensor)
            {
                $('#sensor_elems').append(
                    $('<div/>',
                    {
                        id: 'sensor_elems_'+sensor
                    })
                );

                api_query('sensor/'+sensor, draw_sensor);
            });
        }

        $('#collection_elems_'+collection).parent().siblings().each(function (i, co)
        {
            $(co).removeClass('active');
        });
        $('#collection_elems_'+collection).parent().addClass('active');

        api_query('collection/'+collection, collection_callback);
    }

    function run_table()
    {
        function units_callback(units)
        {
            var wdh = 3;

            $('#unit_elems').html(
                $('<h3/>',
                {
                    class: 'text-centered',
                    text: 'units'
                })
            );

            $.each(units, function (i, unit)
            {
                var elem = (i - (i % wdh));
                var block = (
                    (i % wdh) !== 0 ? $('#unit_elems_block_'+elem) : $('<div/>',
                    {
                        id: 'unit_elems_block_'+elem,
                        class: 'units-row end'
                    })
                ).append(
                    $('<div/>',
                    {
                        class: 'unit-33 text-centered',
                        id: 'unit_elems_'+unit
                    })
                );
                $('#unit_elems').append(block);

                api_query('unit/'+unit, draw_unit);
            });
        }

        function collections_callback(collections)
        {
            $('#collection_elems').text('');

            var draw_num = 0;

            $.each(collections, function (i, collection)
            {
                $('#collection_elems').append(
                    $('<li/>').append(
                        $('<a/>',
                        {
                            id: 'collection_elems_'+collection,
                            text: collection
                        }).on('click', function (cl)
                        {
                            draw_collection(collection);
                        })
                    )
                );

                if (anchor.indexOf(collection) === 0 || i == draw_num)
                {
                    draw_collection(collection);
                }
            });
        }

        api_query('collection', collections_callback);
        api_query('unit', units_callback);
    }

    run_table();
});
