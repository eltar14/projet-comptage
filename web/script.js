function processData(apiData) {
            const labels = Object.keys(apiData);
            const values = Object.values(apiData);
            return { labels, values };
        }
function groupDataByType(apiData) {
            const grouped = {};
            let upCount = 0;
            let downCount = 0;

            for (const [key, value] of Object.entries(apiData)) {
                const [type, direction] = key.split('_');

                grouped[type] = (grouped[type] || 0) + value;

                // Compter les "up" et "down"
                if (direction === 'up') {
                    upCount += value;
                } else if (direction === 'down') {
                    downCount += value;
                }
            }

            return {
                typeLabels: Object.keys(grouped),
                typeValues: Object.values(grouped),
                directionLabels: ['Up', 'Down'],
                directionValues: [upCount, downCount]
            };
        }
async function initialize_pie_chart(){
    try{
        const response = await fetch("http://localhost:5000/counts");
        const json = await response.json()

        const { typeLabels, typeValues, directionLabels, directionValues } = groupDataByType(json.data);


        const typeData = [{
                    values: typeValues,
                    labels: typeLabels,
                    type: 'pie',
                    textinfo: 'label+percent',
                    insidetextorientation: 'radial'
                }];



        const typeLayout = {
                    title: 'Répartition par Type'
                };


        Plotly.newPlot('typePiechart', typeData, typeLayout);



        const directionData = [{
                    values: directionValues,
                    labels: directionLabels,
                    type: 'pie',
                    textinfo: 'label+percent',
                    insidetextorientation: 'radial'
                }];

                const directionLayout = {
                    title: 'Répartition Up/Down'
                };

        Plotly.newPlot('directionPiechart', directionData, directionLayout);

        setInterval(update_charts, 1000);

    }catch (error){
        console.error('Erreur lors de l’initialisation :', error);
    }
}

async function update_charts(){
    try{
        const response = await fetch("http://localhost:5000/counts");
        const json = await response.json()

        const { typeLabels, typeValues, directionLabels, directionValues } = groupDataByType(json.data);

        Plotly.restyle('typePiechart', {
                    labels: [typeLabels],
                    values: [typeValues]
                });


        Plotly.restyle('directionPiechart', {
            labels: [directionLabels],
            values: [directionValues]
        });


    }catch(error){
        console.error('Erreur lors de la mise à jour :', error);
    }
}

initialize_pie_chart()