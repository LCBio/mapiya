function initMolStarViewer(pdburl, viewport_id)
{
    var viewerInstance = new PDBeMolstarPlugin();
    var options =
    {
        customData: 
        {
            url: pdburl ,
            format: 'pdb',
            binary: false 
        },
        hideControls: false,
        bgColor: 
        {
            r:255,
            g:255,
            b:255
        },
        pdbeLink: false,
        landscape: true,
        hideStructure: ['het', 'water', 'carbs', 'nonStandard', 'coarse'],
        subscribeEvents: true,
        expanded: true
        /*
        assemblyId:
        domainAnnotation: false
        encoding: "bcif"
        granularity:
        hideCanvasControls:
        highlightColor:
        landscape: true
        ligandView:
        loadCartoonsOnly: false
        loadMaps: false
        lowPrecisionCoords: false
        mapSettings: undefined
        moleculeId: undfined
        pdbeLink:
        pdbeUrl: "https://www.ebi.ac.uk/pdbe/"
        selectColor:
        selectInteraction: true
        selection:
        superposition:
        superpositionParams:
        validationAnnotation: false
        visualStyle:
        molstar_accessible_surface_area: true,
        */
    };
    var viewerContainer = document.getElementById(viewport_id);
    viewerInstance.render(viewerContainer, options);
    return viewerInstance;
};

function generateChainColourPairs()
{
    var colors_plotly = sessionStorage.getItem("chains-colors");
    var chains_colors = JSON.parse(colors_plotly);
    var selections = [];
    for (var k in chains_colors) 
    {
        var rgba = chains_colors[k].substr(5).split(")")[0].split(",");
        var bg = [255, 255, 255];
        alpha = 1 - rgba[3];
        selections.push(
            {
                struct_asym_id: k.split("-")[1],
                start_residue_number: 0,
                end_residue_number: 0,
                color:
                {
                    r: Math.round((rgba[3] * (rgba[0] / 255) + (alpha * (bg[0] / 255))) * 255),
                    g: Math.round((rgba[3] * (rgba[1] / 255) + (alpha * (bg[1] / 255))) * 255),
                    b: Math.round((rgba[3] * (rgba[2] / 255) + (alpha * (bg[2] / 255))) * 255)
                },
                sideChain: false,
                focus : false
            }
        );
    };

    return selections;
};

function updateMolStarViewer(viewerInstance)
{
    var selectSections = generateChainColourPairs();
    viewerInstance.visual.select(
    {
        data: selectSections,
        nonSelectedColor: 
        {
            r:255,
            g:255,
            b:255
        }
    });
}