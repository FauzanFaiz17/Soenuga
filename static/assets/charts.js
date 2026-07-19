import ApexCharts from 'apexcharts';

const getMainChartOptions = () => {
    let mainChartColors = {}

    if (document.documentElement.classList.contains('dark')) {
        mainChartColors = {
            borderColor: '#374151',
            labelColor: '#9CA3AF',
            opacityFrom: 0,
            opacityTo: 0.15,
        };
    } else {
        mainChartColors = {
            borderColor: '#F3F4F6',
            labelColor: '#6B7280',
            opacityFrom: 0.45,
            opacityTo: 0,
        }
    }

    return {
        chart: {
            height: 420,
            type: 'area',
            fontFamily: 'Inter, sans-serif',
            foreColor: mainChartColors.labelColor,
            toolbar: {
                show: false
            }
        },
        fill: {
            type: 'gradient',
            gradient: {
                enabled: true,
                opacityFrom: mainChartColors.opacityFrom,
                opacityTo: mainChartColors.opacityTo
            }
        },
        dataLabels: {
            enabled: false
        },
        tooltip: {
            style: {
                fontSize: '14px',
                fontFamily: 'Inter, sans-serif',
            },
        },
        grid: {
            show: true,
            borderColor: mainChartColors.borderColor,
            strokeDashArray: 1,
            padding: {
                left: 35,
                bottom: 15
            }
        },
        series: [
            {
                name: 'Pemasukan',
                data: income,
                color: '#10B981'
            },
            {
                name: 'Pengeluaran',
                data: expense,
                color: '#EF4444'
            },
            {
                name: 'Saldo',
                data: balance,
                color: '#1A56DB'
            }
        ],
        markers: {
            size: 5,
            strokeColors: '#ffffff',
            hover: {
                size: undefined,
                sizeOffset: 3
            }
        },
        xaxis: {
            categories: labels,
            labels: {
                style: {
                    colors: [mainChartColors.labelColor],
                    fontSize: '14px',
                    fontWeight: 500,
                },
            },
            axisBorder: {
                color: mainChartColors.borderColor,
            },
            axisTicks: {
                color: mainChartColors.borderColor,
            },
            crosshairs: {
                show: true,
                position: 'back',
                stroke: {
                    color: mainChartColors.borderColor,
                    width: 1,
                    dashArray: 10,
                },
            },
        },
        yaxis: {
            labels: {
                style: {
                    colors: [mainChartColors.labelColor],
                    fontSize: '14px',
                    fontWeight: 500,
                },
                formatter: function (value) {
                    return 'Rp' + value;
                }
            },
        },
        legend: {
            fontSize: '14px',
            fontWeight: 500,
            fontFamily: 'Inter, sans-serif',
            labels: {
                colors: [mainChartColors.labelColor]
            },
            itemMargin: {
                horizontal: 10
            }
        },
        responsive: [
            {
                breakpoint: 1024,
                options: {
                    xaxis: {
                        labels: {
                            show: false
                        }
                    }
                }
            }
        ]
    };
}

if (document.getElementById('finance-chart')) {
    const chart = new ApexCharts(document.getElementById('finance-chart'), getMainChartOptions());
    chart.render();

    // init again when toggling dark mode
    document.addEventListener('dark-mode', function () {
        chart.updateOptions(getMainChartOptions());
    });
}

if (document.getElementById('new-products-chart')) {
    const options = {
        colors: ['#1A56DB', '#FDBA8C'],
        series: [
            {
                name: 'Quantity',
                color: '#1A56DB',
                data: [
                    { x: '01 Feb', y: 170 },
                    { x: '02 Feb', y: 180 },
                    { x: '03 Feb', y: 164 },
                    { x: '04 Feb', y: 145 },
                    { x: '05 Feb', y: 194 },
                    { x: '06 Feb', y: 170 },
                    { x: '07 Feb', y: 155 },
                ]
            }
        ],
        chart: {
            type: 'bar',
            height: '140px',
            fontFamily: 'Inter, sans-serif',
            foreColor: '#4B5563',
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            bar: {
                columnWidth: '90%',
                borderRadius: 3
            }
        },
        tooltip: {
            shared : false,
            intersect: false,
            style: {
                fontSize: '14px',
                fontFamily: 'Inter, sans-serif'
            },
        },
        states: {
            hover: {
                filter: {
                    type: 'darken',
                    value: 1
                }
            }
        },
        stroke: {
            show: true,
            width: 5,
            colors: ['transparent']
        },
        grid: {
            show: false
        },
        dataLabels: {
            enabled: false
        },
        legend: {
            show: false
        },
        xaxis: {
            floating: false,
            labels: {
                show: false
            },
            axisBorder: {
                show: false
            },
            axisTicks: {
                show: false
            },
        },
        yaxis: {
            show: false
        },
        fill: {
            opacity: 1
        }
    };

    const chart = new ApexCharts(document.getElementById('new-products-chart'), options);
    chart.render();
}

const getVisitorsChartOptions = () => {
    let visitorsChartColors = {}

    if (document.documentElement.classList.contains('dark')) {
        visitorsChartColors = {
            fillGradientShade: 'dark',
            fillGradientShadeIntensity: 0.45,
        };
    } else {
        visitorsChartColors = {
            fillGradientShade: 'light',
            fillGradientShadeIntensity: 1,
        }
    }

    return {
        series: [{
            name: 'Visitors',
            data: [500, 590, 600, 520, 610, 550, 600]
        }],
        labels: ['01 Feb', '02 Feb', '03 Feb', '04 Feb', '05 Feb', '06 Feb', '07 Feb'],
        chart: {
            type: 'area',
            height: '305px',
            fontFamily: 'Inter, sans-serif',
            sparkline: {
                enabled: true
            },
            toolbar: {
                show: false
            }
        },
        fill: {
            type: 'gradient',
            gradient: {
                shade: visitorsChartColors.fillGradientShade,
                shadeIntensity: visitorsChartColors.fillGradientShadeIntensity
            },
        },
        plotOptions: {
            area: {
                fillTo: 'end'
            }
        },
        theme: {
            monochrome: {
                enabled: true,
                color: '#1A56DB',
            }
        },
        tooltip: {
            style: {
                fontSize: '14px',
                fontFamily: 'Inter, sans-serif'
            },
        },
    }
}


const getSignupsChartOptions = () => {
    let signupsChartColors = {}

    if (document.documentElement.classList.contains('dark')) {
        signupsChartColors = {
            backgroundBarColors: ['#374151', '#374151', '#374151', '#374151', '#374151', '#374151', '#374151']
        };
    } else {
        signupsChartColors = {
            backgroundBarColors: ['#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB']
        };
    }

    return {
        series: [{
            name: 'Users',
            data: [1334, 2435, 1753, 1328, 1155, 1632, 1336]
        }],
        labels: ['01 Feb', '02 Feb', '03 Feb', '04 Feb', '05 Feb', '06 Feb', '07 Feb'],
        chart: {
            type: 'bar',
            height: '140px',
            foreColor: '#4B5563',
            fontFamily: 'Inter, sans-serif',
            toolbar: {
                show: false
            }
        },
        theme: {
            monochrome: {
                enabled: true,
                color: '#1A56DB'
            }
        },
        plotOptions: {
            bar: {
                columnWidth: '25%',
                borderRadius: 3,
                colors: {
                    backgroundBarColors: signupsChartColors.backgroundBarColors,
                    backgroundBarRadius: 3
                },
            },
            dataLabels: {
                hideOverflowingLabels: false
            }
        },
        xaxis: {
            floating: false,
            labels: {
                show: false
            },
            axisBorder: {
                show: false
            },
            axisTicks: {
                show: false
            },
        },
        tooltip: {
            shared: true,
            intersect: false,
            style: {
                fontSize: '14px',
                fontFamily: 'Inter, sans-serif'
            }
        },
        states: {
            hover: {
                filter: {
                    type: 'darken',
                    value: 0.8
                }
            }
        },
        fill: {
            opacity: 1
        },
        yaxis: {
            show: false
        },
        grid: {
            show: false
        },
        dataLabels: {
            enabled: false
        },
        legend: {
            show: false
        },
    };
}



const pieChartOptions = (data) => {

    let trafficChannelsChartColors = {}

    if (document.documentElement.classList.contains('dark')) {
        trafficChannelsChartColors = {
            strokeColor: '#1f2937'
        };
    } else {
        trafficChannelsChartColors = {
            strokeColor: '#ffffff'
        }
    }

    return {
        series: data.map(dt => dt.price),
        labels: data.map(dt => dt.name),
        colors: ['#16BDCA', '#FDBA8C', '#1A56DB'],
        chart: {
            type: 'donut',
            height: 400,
            fontFamily: 'Inter, sans-serif',
            toolbar: {
                show: false
            },
        },
        responsive: [{
            breakpoint: 430,
            options: {
              chart: {
                height: 300
              }
            }
        }],
        stroke: {
            colors: [trafficChannelsChartColors.strokeColor]
        },
        states: {
            hover: {
                filter: {
                    type: 'darken',
                    value: 0.9
                }
            }
        },
        tooltip: {
            shared: true,
            followCursor: false,
            fillSeriesColor: false,
            inverseOrder: true,
            style: {
                fontSize: '14px',
                fontFamily: 'Inter, sans-serif'
            },
            x: {
                show: true,
                formatter: function (_, { seriesIndex, w }) {
                    const label = w.config.labels[seriesIndex];
                    return label
                }
            },
            y: {
                formatter: function (value) {
                    return value;
                }
            }
        },
        grid: {
            show: false
        },
        dataLabels: {
            enabled: false
        },
        legend: {
            show: false
        },
    };
}


// ════════════════════════════════════════════════════════════
// FINANCE CHART — Halaman Keuangan Soenuga
// Sumber data: hidden <script id="..."> yang di-render Django
// di template finance/index.html (lihat _get_chart_data di views.py)
// ════════════════════════════════════════════════════════════

const labels = JSON.parse(
    document.getElementById("months-labels").textContent
);

const income = JSON.parse(
    document.getElementById("income-data").textContent
);

const expense = JSON.parse(
    document.getElementById("expense-data").textContent
);

const getFinanceChartOptions = () => {
    return {
        chart: {
            type: "line",
            height: 380
        },
        series: [
            {
                name: "Test",
                data: [10, 20, 30, 40, 50, 60]
            }
        ],
        xaxis: {
            categories: ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun"]
        }
    };
};

const financeElement = document.getElementById("finance-chart");

console.log("financeElement:", financeElement);

if (financeElement) {

    console.log("Masuk IF");

    const options = getFinanceChartOptions();

    console.log("Options:", options);

    const chart = new ApexCharts(financeElement, options);

    console.log("Chart dibuat");

    chart.render().then(() => {
        console.log("Render selesai");

        console.log(financeElement.innerHTML);
    }).catch(err => {
        console.error(err);
    });

}
