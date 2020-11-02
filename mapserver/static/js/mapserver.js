// helper function used to insert csrf token into ajax post data
let getCookie = function (name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// helper function to check if jQuery returns undefined
$.fn.exists = function () {
    return this.length !== 0;
};

//------------------------------- BEGIN Map class -----------------------------

const DEFAULT_CONTACT_CUTOFF = 4.5;

class Map {

    constructor(data) {
        this.data = data.info;
        this.triup = data.matrix;
        this.title = data.title;
        this.lengths = [];
        this.labels = [];

        this.dim = 0;
        for (let obj of this.data) {
            this.dim += obj.residues.length;
            this.lengths.push(obj.residues.length);
            this.labels.push(...obj.residues);
        }
        this.diagonal = this.makeDiagonal();
        this.diagSeries = this.makeDiagSeries();
        this.offDiagSeries = this.makeOffDiagSeries();
        this.contactSeries = this.makeContactSeries(DEFAULT_CONTACT_CUTOFF);
    }

    matrix(x, y) {
        if (x > y) {
            return this.triup[0.5 * y * (2 * this.dim - 3 - y) + x - 1];
        } else if (x < y) {
            return this.matrix(y, x);
        } else {
            return 0.0;
        }
    }

    makeDiagonal() {
        let data = [];
        for (let i = 0; i < this.dim; ++i)
            data.push([i, i, 1]);
        return {
            data: data,
            colorAxis: null,
            color: '#000000',
            showInLegend: false,
            boostThreshold: 1
        }
    }

    makeDiagSeries() {
        let series = [];
        let start = 0;
        for (let id = 0; id < this.lengths.length; ++id) {
            let data = [];
            let stop = start + this.lengths[id];
            for (let j = start; j < stop; ++j) {
                for (let i = j + 1; i < stop; ++i) {
                    data.push([i, j, this.matrix(i, j)]);
                }
            }
            start = stop;
            series.push({
                name: 'D_' + id,
                data: data,
                colorAxis: 0,
                boostThreshold: 1
            });
        }
        return series;
    }

    makeOffDiagSeries() {
        let series = [];
        let startY = 0;
        for (let jd = 0; jd < this.lengths.length - 1; ++jd) {
            let stopY = startY + this.lengths[jd];
            let startX = stopY;
            for (let id = jd + 1; id < this.lengths.length; ++id) {
                let data = [];
                let stopX = startX + this.lengths[id];
                for (let j = startY; j < stopY; ++j)
                    for (let i = startX; i < stopX; ++i)
                        data.push([i, j, this.matrix(i, j)]);
                series.push({
                    name: 'D_' + id + ':' + jd,
                    data: data,
                    colorAxis: 0,
                    boostThreshold: 1
                });
                startX = stopX;
            }
            startY = stopY
        }
        return series;
    }

    makeContactSeries(cutoff) {
        let series = [];
        let distanceSeries = [...this.diagSeries, ...this.offDiagSeries];
        for (let serie of distanceSeries) {
            let data = [];
            for (let d of serie.data) {
                if (d[2] < cutoff) {
                    data.push([d[1], d[0], 1]);
                }
            }
            series.push({
                name: serie.name,
                data: data,
                colorAxis: null,
                color: '#002aff',
                showInLegend: true
            });
        }

        return series;
    }

    getSeries() {
        return [this.diagonal, ...this.diagSeries, ...this.offDiagSeries, ...this.contactSeries];
    }
}

//------------------------------- END Map class -------------------------------

let fitHeight = function (viewport_id) {
    let offset = 200;
    $('#' + viewport_id).height($(window).innerHeight() - offset);
};

let initChart = function (map_pk, viewport_id) {
    fitHeight(viewport_id);

    $(window).resize(function () {
        fitHeight(viewport_id);
    });

    let $viewport = $('#' + viewport_id);
    $.getJSON('/map/' + map_pk + '/data/', function (data) {
        let map = new Map(data);
        let chart = Highcharts.chart(viewport_id, {

            chart: {
                plotBorderWidth: 1,

                type: 'heatmap',
                zoomType: 'xy',
                boost: {
                    useGPUTranslations: true
                }
            },

            title: {
                text: map.title
            },

            series: map.getSeries(),

            plotOptions: {
                series: {
                    boostThreshold: 0,
                    events: {
                        click: function (event) {
                            series = chart.series;
                            for (let i = 0; i < series.length; i++) {
                                series[i].hide();
                            }
                            this.show();
                            // chart.redraw();
                        }
                    }
                }
            },

            tooltip: {
                formatter: function () {
                    return map.labels[this.point.x] + ' ' + map.labels[this.point.y];
                }
            },

            xAxis: {
                // min: 0,
                // max: map.dim - 1,
                tickInterval: 1,
                labels: {
                    rotation: -90,
                    formatter: function () {
                        return map.labels[this.value];
                    }
                }
            },

            yAxis: {
                // min: 0,
                // max: map.dim - 1,
                tickInterval: 1,
                scrollbar: {
                    enabled: true
                },
                tickWidth: 1,
                gridLineWidth: 0,
                title: {text: null},
                labels: {
                    formatter: function () {
                        return map.labels[this.value];
                    }
                }
            },

            colorAxis: {
                stops: [
                    [0, '#c4463a'],
                    [0.5, '#fffbbc'],
                    [0.9, '#3060cf'],
                ]
            }
        });

    }).fail(function () {
        $viewport.append('<h1>Error</h1>');
    });
}

let initNGL = function (pdburl, viewport_id) {
    fitHeight(viewport_id);
    let $nglMenu = $('div.ngl-menu');
    let $icon = $('#nglMenuIcon');
    let $table = $nglMenu.find('table');
    let csrftoken = getCookie('csrftoken');
    let stage = new NGL.Stage(viewport_id, {backgroundColor: 'white'})
    representations = {};
    let struct;

    stage.loadFile(pdburl).then(function (o) {
        struct = o;

        $table.find('tbody').find('tr').each(function () {
            let key = $(this).attr('id');
            mkRepresentation(key);
        });

        o.autoView();
        $('.ngl-bottom-menu').css('visibility', 'visible');
    });

    $(window).resize(function () {
        fitHeight(viewport_id);
        stage.handleResize();
    });

    // onhover event handler for ngl menu on the right
    $nglMenu.hover(function () {
        $nglMenu.addClass('active');
        $icon.addClass('d-none');
        $table.removeClass('d-none');
    }, function () {
        $nglMenu.removeClass('active');
        $icon.removeClass('d-none');
        $table.addClass('d-none');
    });

    // "click on link within NGL table" event handler
    $table.on('click', 'a.ngl-cmd', function (event) {
        event.preventDefault();
        $.ajax({
            headers: {"X-CSRFToken": csrftoken},
            url: $(this).attr('href'),
            method: 'POST',
            success: function (data) {
                if (data.error) {
                    alert(data.error);
                    // TODO: perhaps some nicer way to show errors
                } else if (data.addRep) {
                    let $newRow = $(data.addRep);
                    let key = $newRow.attr('id');
                    $table.find('tbody').append($newRow);
                    mkRepresentation(key);
                } else if (data.delRep) {
                    let key = data.delRep;
                    rmRepresentation(key);
                    $table.find('tr#' + key).remove();
                }
            }
        });
    });

    // "onchange" event handler for inputs and selects within NGL table
    $table.on('change', '.ngl-input', function () {
        let key = $(this).parents('tr').attr('id');
        let pk = key.split('_').pop();
        let dataobj = {
            'name': $(this).attr('name'),
            'value': $(this).val()
        };
        $.ajax({
            headers: {"X-CSRFToken": csrftoken},
            url: '/ngl/' + pk + '/update/',
            method: 'POST',
            data: dataobj,
            success: function (data) {
                if (data.error) {
                    alert(data.error);
                } else if (data.updateRep) {
                    let key = data.updateRep;
                    rmRepresentation(key);
                    mkRepresentation(key);
                }
            }
        })
    });

    // toggle representation visibility event handler
    $table.on('click', 'a.ngl-eye', function () {
        let $icon = $(this).find('i');
        let key = $(this).parents('tr').attr('id');
        $icon.toggleClass(['fa-eye', 'fa-eye-slash']);
        representations[key].toggleVisibility();
    });

    // handler for on onclick event on the "cog" icon
    $table.on('click', 'a.ngl-options', function (event) {
        event.preventDefault();
        let url = $(this).attr('href');

        // current table row
        let $tr = $(this).parents('tr');
        let keyword = $(this).data('keyword');

        // next table row
        let $options = $tr.next();

        // if next row exists and has data-keyword attribute
        if ($options.exists() && $options.data('keyword')) {

            // if keywords match remove next row
            if ($options.data('keyword') === keyword) {
                $options.remove();
            }

        // create options panel as the next row in the table
        } else {
            $options = $('<tr><td colspan="5"><div></div></td></tr>');
            $options.insertAfter($tr);
        }

        // if panel options exists fill it with data fetched from the url and insert after current row
        if ($options.exists()) {
            $.ajax({
                url: url,
                method: 'GET',
                data: {keyword: keyword},
                success: function (data) {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        $options.data('keyword', keyword);
                        $options.find('div').html(data.html);
                    }
                }
            });
        }

    });

    // function which removes options panel when new type of representation is selected
    $table.on('change', 'select[name="representation"]', function () {
        let $options = $(this).parents('tr').next();
        if ($options.exists() && $options.data('keyword')) {
            if ($options.data('keyword') === 'representation') {
                $options.remove();
            }
        }
    });

    let fetchFromTable = function(key) {
        let $currentTr = $table.find('tr#' + key);
        return {
            'name': $currentTr.find('[name="name"]').val(),
            'color': $currentTr.find('[name="color"]').val(),
            'representation': $currentTr.find('[name="representation"]').val(),
            'selection': $currentTr.find('[name="selection"]').val()
        }
    };
    
    let rmRepresentation = function(key) {
        let rep = representations[key];
        struct.removeRepresentation(rep);
        delete representations[key];
    };

    let mkRepresentation = function(key) {
        let data = fetchFromTable(key);
        let pk = key.split('_').pop();
        let options = {};
        $.getJSON('/ngl/' + pk + '/options/', function (data) {
            options = data;
        });
        representations[key] = struct.addRepresentation(data.representation, Object.assign({}, {
            name: data.name,
            colorScheme: data.color,
            sele: data.selection,
        }, options));
    };

    $('#colorPicker').on('change', 'input', function () {
        stage.setParameters( { backgroundColor: $(this).val() } );
    });

    $('#fullScreen').on('click', function () {
        stage.toggleFullscreen();
    });

    $('#toggleSpin').on('click', function () {
        stage.toggleSpin();
    });

    $('#center').on('click', function () {
        stage.autoView();
    });

};
