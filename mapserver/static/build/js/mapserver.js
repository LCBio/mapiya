// js for map-detail view

var init_map_detail = function (pdburl, dataurl) {

    var stage = new NGL.Stage("viewport", {backgroundColor:'white'});

    var defaultCutoff = 10;

    $('#slider').bind('click', function () {
        isContact = true;
        chart.colorAxis[0].update({
            dataClassColor: 'category',
            dataClasses: [{
                to: this.value
            }, {
                from: this.value
            }]
        });
        chart.legend.update({
            title: {
                text: ''
            },
            align: 'right',
            verticalAlign: 'top',
            floating: false,
            y: 50,
            layout: 'vertical',
            valueDecimals: 0,
            backgroundColor: 'rgba(255,255,255,0.9)',
            symbolRadius: 0,
            symbolHeight: 14
        });
    });

    var options = {
        chart: {
            zoomType: 'xy',
            panning: true,
            panKey: 'shift',
            defaultSeriesType: 'heatmap'
        },
        title: {
            text: 'Click and drag to zoom in. Hold down ctrl key to select multiple.'
        },


        xAxis: {
            gridLineWidth: 0,
            categories: [],
            events:{
                'afterSetExtremes': function () {
                    var min, max;
                    ({min, max} = chart.axes[0].getExtremes());
                    var diff = max - min;
                    if (diff < 30) {
                        chart.series[0].update({'boostThreshold': 0});
                    }
                }
            }
        },
        yAxis: {
            gridLineWidth: 0,
            title: {
                text: null
            },
            categories: []

        },


        colorAxis: {
            dataClassColor: 'category',
            dataClasses: [{
                to: defaultCutoff
            }, {
                from: defaultCutoff
            }]
        },


        tooltip: {
            formatter: function () {
            return '<b>' + this.point.xNgl + '</b>  <br><b>' +
                this.point.yNgl + '</b> <br><b>Disctance: ' + this.point.value + '	\u212B</b>';
            }
        },


        plotOptions: {
            series: {
                marker: {
                    enabled: true
                },
                animation:false,
                states: {
                    hover: {
                        enabled: false
                    }
                },
                cursor: 'pointer',
                events: {
                    click: function (event) {
                        if (event.ctrlKey) {
                            kopytka = kopytka.concat(event.point.xNgl.toString(), ' or ', event.point.yNgl.toString(), ' or ');
                            event.point.select(false, true);
                            if (wasSolo) {
                                chart.getSelectedPoints()[0].select(false);
                            }

                            if (!isRepStyle3) {
                                repstyle3 = struct1.addRepresentation("licorice", {colorScheme: "atomindex"});
                                repstyle3.setSelection(event.point.xNgl.toString() + ' or ' + event.point.yNgl.toString());
                                isRepStyle3 = true;
                                wasSolo = false;
                            } else {
                                struct1.removeRepresentation(repstyle3);
                                repstyle3 = struct1.addRepresentation("licorice", {colorScheme: "atomindex"});
                                repstyle3.setSelection(kopytka.toString());
                                isRepStyle3 = true;
                                wasSolo = false;

                            }

                        } else {
                            kopytka = '';
                            if (!isRepStyle3) {
                                repstyle3 = struct1.addRepresentation("licorice", {colorScheme: "atomindex"});
                                repstyle3.setSelection(event.point.xNgl.toString() + ' or ' + event.point.yNgl.toString());
                                isRepStyle3 = true;
                                wasSolo = true;
                            } else {
                                struct1.removeRepresentation(repstyle3);
                                repstyle3 = struct1.addRepresentation("licorice", {colorScheme: "atomindex"});
                                repstyle3.setSelection(event.point.xNgl.toString() + ' or ' + event.point.yNgl.toString());
                                isRepStyle3 = true;
                                wasSolo = true;
                            }

                        }



                    },

                },
            }
        },


        mapNavigation: {
            enableMouseWheelZoom: true
        },

        legend: {
            title: {
                text: ''
            },
            align: 'right',
            verticalAlign: 'top',
            floating: false,
            y: 50,
            layout: 'vertical',
            valueDecimals: 0,
            backgroundColor: 'rgba(255,255,255,0.9)',
            symbolRadius: 0,
            symbolHeight: 14
        },
        series: []
    };


    Highcharts.ajax({
        url: dataurl,
        success: function (data) {
            console.log(data.points.length)
            if (data.success) {
                options.series.push({
                    data: data.points,
                    allowPointSelect: true,
                    turboThreshold: [data.points.length ],
                    boostThreshold: 900,
                    states: {
                        select: {
                            color: 'red',
                            borderWidth: 5,
                            borderColor: 'Black'
                        },
                    }
                });
                options.xAxis.categories=data.labels;
                options.yAxis.categories=data.labels;
                window.chart = Highcharts.chart('chartViewport', options);
            } else {
                console.log('View returned no data');
            }
        },
        error: function (e, t) {
            console.error(e, t);
        }
    });


    stage.loadFile(pdburl).then(function (o) {
        struct1 = o;
        basicRep = o.addRepresentation("cartoon", {colorScheme: "element"});
        o.autoView();
    });

    var resetView = document.getElementById("resetView");
    resetView.addEventListener("click", function () {
        stage.autoView();
    });

    var toggleTheme = document.getElementById( "toggleTheme" );
    toggleTheme.addEventListener( "mouseout", function(){
        stage.setParameters( { backgroundColor: toggleTheme.value } );
    } );

    var toggleSpin = document.getElementById("toggleSpin");
    var isSpinning = false;
    toggleSpin.addEventListener("click", function () {
        if (!isSpinning) {
            stage.setSpin([0, 1, 0], 0.01);
            isSpinning = true;
        } else {
            stage.setSpin(null, null);
            isSpinning = false;
        }
    });

    var fullscreen = document.getElementById("fullscreen");
    fullscreen.addEventListener("click", function () {
        stage.toggleFullscreen();
    });


    var selectLabelStyle = document.getElementById("selectLabelStyle");
    var isLabelStyle = false;
    selectLabelStyle.addEventListener("click", function () {
        if (!isLabelStyle) {
            labstyle = struct1.addRepresentation("label", {labelType: selectLabelStyle.value});
            labstyle.setSelection(inputLabelSelection.value);
            isLabelStyle = true;
        } else {
            struct1.removeRepresentation(labstyle);
            labstyle = struct1.addRepresentation("label", {labelType: selectLabelStyle.value});
            labstyle.setSelection(inputLabelSelection.value);
            isLabelStyle = true;
        }
    });

    var inputLabelSelection = document.getElementById("inputLabelSelection");
    inputLabelSelection.addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            if (!isLabelStyle) {
                labstyle = struct1.addRepresentation("label", {labelType: selectLabelStyle.value});
                labstyle.setSelection(inputLabelSelection.value);
                isLabelStyle = true;
            } else {
                struct1.removeRepresentation(labstyle);
                labstyle = struct1.addRepresentation("label", {labelType: selectLabelStyle.value});
                labstyle.setSelection(inputLabelSelection.value);
                isLabelStyle = true;
            }
        }
    });

    var closeLabels = document.getElementById("closeLabels");
    closeLabels.addEventListener("click", function () {
        struct1.removeRepresentation(labstyle);
    });


    var wasSolo = false;

    var selectRepStyle1 = document.getElementById("selectRepStyle1");
    var isRepStyle1 = false;
    selectRepStyle1.addEventListener("click", function () {
        if (!isRepStyle1) {
            struct1.removeRepresentation(basicRep);
            repstyle1 = struct1.addRepresentation(selectRepStyle1.value, {colorScheme: coloringMethod1.value});
            repstyle1.setSelection(inputRepStyle1.value);
            isRepStyle1 = true;
        } else {
            struct1.removeRepresentation(repstyle1);
            repstyle1 = struct1.addRepresentation(selectRepStyle1.value, {colorScheme: coloringMethod1.value});
            repstyle1.setSelection(inputRepStyle1.value);
            isRepStyle1 = true;
        }
    });


    var kopytka = '';

    var inputRepStyle1 = document.getElementById("inputRepStyle1");
    inputRepStyle1.addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            if (!isRepStyle1) {
                struct1.removeRepresentation(basicRep);
                repstyle1 = struct1.addRepresentation(selectRepStyle1.value, {colorScheme: coloringMethod1.value});
                repstyle1.setSelection(inputRepStyle1.value);
                isRepStyle1 = true;
            } else {
                struct1.removeRepresentation(repstyle1);
                repstyle1 = struct1.addRepresentation(selectRepStyle1.value, {colorScheme: coloringMethod1.value});
                repstyle1.setSelection(inputRepStyle1.value);
                isRepStyle1 = true;
            }
        }
    });


    var coloringMethod1 = document.getElementById("coloringMethod1");
    coloringMethod1.addEventListener("click", function () {
        if (!isRepStyle1) {
            struct1.removeRepresentation(basicRep);
            repstyle1 = struct1.addRepresentation(selectRepStyle1.value, {colorScheme: coloringMethod1.value});
            repstyle1.setSelection(inputRepStyle1.value);
            isRepStyle1 = true;
        } else {
            struct1.removeRepresentation(repstyle1);
            repstyle1 = struct1.addRepresentation(selectRepStyle1.value, {colorScheme: coloringMethod1.value});
            repstyle1.setSelection(inputRepStyle1.value);
            isRepStyle1 = true;
        }
    });

    var closeRep1 = document.getElementById("closeRep1");
    closeRep1.addEventListener("click", function () {
        struct1.removeRepresentation(basicRep);
        struct1.removeRepresentation(repstyle1);

    });


    var lenMap = document.getElementById("lenMap");
    var isContact = true;
    lenMap.addEventListener("click", function () {
        if (isContact) {
            isContact = false;
            chart.colorAxis[0].update({
                dataClassColor: '',
                dataClasses: '',
                min: 0,
                minColor: '#FFFFFF',
                maxColor: Highcharts.getOptions().colors[0]
            });
            chart.legend.update({
                align: 'right',
                layout: 'vertical',
                margin: 0,
                verticalAlign: 'top',
                y: 25,
                symbolHeight: 280
            });
        } else {
            isContact = true;
            chart.colorAxis[0].update({
                dataClassColor: 'category',
                dataClasses: [{
                    to: defaultCutoff
                }, {
                    from: defaultCutoff
                }]
            });
            chart.legend.update({
                title: {
                    text: ''
                },
                align: 'right',
                verticalAlign: 'top',
                floating: false,
                y: 50,
                layout: 'vertical',
                valueDecimals: 0,
                backgroundColor: 'rgba(255,255,255,0.9)',
                symbolRadius: 0,
                symbolHeight: 14
            });
        }
    });


    var closeRep3 = document.getElementById("closeRep3");
    closeRep3.addEventListener("click", function () {
        struct1.removeRepresentation(repstyle3);
        kopytka = '';
        chart.getSelectedPoints()[0].select(false);
    });


    var selectRepStyle2 = document.getElementById("selectRepStyle2");
    var isRepStyle2 = false;
    selectRepStyle2.addEventListener("click", function () {
        if (!isRepStyle2) {
            repstyle2 = struct1.addRepresentation(selectRepStyle2.value, {colorScheme: coloringMethod2.value});
            repstyle2.setSelection(inputRepStyle2.value);
            isRepStyle2 = true;
        } else {
            struct1.removeRepresentation(repstyle2);
            repstyle2 = struct1.addRepresentation(selectRepStyle2.value, {colorScheme: coloringMethod2.value});
            repstyle2.setSelection(inputRepStyle2.value);
            isRepStyle2 = true;
        }
    });

    $('#someButton').on('click', function () {
        chart.series[0].update({
            'boostThreshold': 1
        });
    });

    var inputRepStyle2 = document.getElementById("inputRepStyle2");
    inputRepStyle2.addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            if (!isRepStyle2) {
                repstyle2 = struct1.addRepresentation(selectRepStyle2.value, {colorScheme: coloringMethod2.value});
                repstyle2.setSelection(inputRepStyle2.value);
                isRepStyle2 = true;
            } else {
                struct1.removeRepresentation(repstyle2);
                repstyle2 = struct1.addRepresentation(selectRepStyle2.value, {colorScheme: coloringMethod2.value});
                repstyle2.setSelection(inputRepStyle2.value);
                isRepStyle2 = true;
            }
        }
    });


    var coloringMethod2 = document.getElementById("coloringMethod2");
    coloringMethod2.addEventListener("click", function () {
        if (!isRepStyle2) {
            struct1.removeRepresentation(basicRep);
            repstyle2 = struct1.addRepresentation(selectRepStyle2.value, {colorScheme: coloringMethod2.value});
            repstyle2.setSelection(inputRepStyle2.value);
            isRepStyle2 = true;
        } else {
            struct1.removeRepresentation(repstyle2);
            repstyle2 = struct1.addRepresentation(selectRepStyle2.value, {colorScheme: coloringMethod2.value});
            repstyle2.setSelection(inputRepStyle2.value);
            isRepStyle2 = true;
        }
    });

    var closeRep2 = document.getElementById("closeRep2");
    closeRep2.addEventListener("click", function () {
        struct1.removeRepresentation(repstyle2);

    });


    var selectRepStyle3 = document.getElementById("selectRepStyle3");
    var isRepStyle3 = false;
//     selectRepStyle3.addEventListener("click", function () {
//         if (!isRepStyle3) {
//             struct1.removeRepresentation(basicRep);
//             repstyle3 = struct1.addRepresentation(selectRepStyle3.value, {colorScheme: coloringMethod3.value});
//             repstyle3.setSelection(inputRepStyle3.value);
//             isRepStyle3 = true;
//         } else {
//             struct1.removeRepresentation(repstyle3);
//             repstyle3 = struct1.addRepresentation(selectRepStyle3.value, {colorScheme: coloringMethod3.value});
//             repstyle3.setSelection(inputRepStyle3.value);
//             isRepStyle3 = true;
//         }
//     });
//
//
//     var inputRepStyle3 = document.getElementById("inputRepStyle3");
//     inputRepStyle3.addEventListener("keyup", function (event) {
//         if (event.keyCode === 13) {
//             repstyle3.setSelection(inputRepStyle3.value);
//         }
//     });
//
//
//     var coloringMethod3 = document.getElementById("coloringMethod3");
//     coloringMethod3.addEventListener("click", function () {
//         if (!isRepStyle3) {
//             struct1.removeRepresentation(basicRep);
//             repstyle3 = struct3.addRepresentation(selectRepStyle3.value, {colorScheme: coloringMethod3.value});
//             repstyle3.setSelection(inputRepStyle3.value);
//             isRepStyle3 = true;
//         } else {
//             struct1.removeRepresentation(repstyle3);
//             repstyle3 = struct1.addRepresentation(selectRepStyle3.value, {colorScheme: coloringMethod3.value});
//             repstyle3.setSelection(inputRepStyle3.value);
//             isRepStyle3 = true;
//         }
//     });
//
//     closeRep3 = document.getElementById("closeRep3");
//     closeRep3.addEventListener("click", function () {
//         struct1.removeRepresentation(basicRep);
//         struct1.removeRepresentation(repstyle3);
//
//     });
};

