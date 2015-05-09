function byte_fmt(bytes)
{
    var units = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
    if(bytes === 0 || bytes == 0){ return '0 Bit'; }
    var i = parseInt(Math.floor(Math.log(bytes)/Math.log(1024)), 10);
    return Math.round(bytes/Math.pow(1024, i), 2) + ' ' + units[i];
}

function time_fmt(seconds)
{
    return moment(seconds).format('DD.MM - HH:mm:ss');
}

function reltime_fmt(seconds)
{
    return moment(seconds).fromNow();
}

function uptime_fmt(seconds)
{
    return moment.duration(seconds, 'seconds').humanize();
}

function rand_num(max, min)
{
    return Math.floor(Math.random() * (max - min) + min);
}

function refresh_seconds()
{
    return rand_num({{ the_autoref_max }}, {{ the_autoref_min }});
}

function api_query(endpoint, callb, method, data, errorcallb)
{
    method = (method ? method : 'GET');
    $('#loader').html(
        $('<i/>', {
            class: 'fa fa-minus'
        })
    ).removeClass('hide').fadeIn('fast');
    function scb (cdt)
    {
        if (cdt !== null && cdt !== undefined)
        {
            $('#loader').fadeOut('fast').addClass('hide');
            return callb(cdt)
        }
    }
    function ecb (ex, err, exp)
    {
        $('#loader').text(exp);
        $('#loader').removeClass('hide').fadeIn('fast');
    }

    $.ajax({
        url: '{{ url_for('api') }}/'+endpoint,
        type: method,
        data: data,
        error: (errorcallb ? errorcallb : ecb),
        success: scb
    });
}

