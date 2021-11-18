function initMolStarViewer(pdburl, viewport_id)
{
    var viewerInstance = new PDBeMolstarPlugin();
    var options =
    {
        customData: { url: pdburl , format: 'pdb', binary: false },
        hideControls: false,
        bgColor: {r:255,g:255,b:255},
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
        */
        /* molstar_accessible_surface_area: true, */

    };
    var viewerContainer = document.getElementById(viewport_id);
    viewerInstance.render(viewerContainer, options);
    return viewerInstance;
};

class getClickMapFromPlotly
{
    constructor()
    {

        this.click_map = document.getElementsByTagName("iframe")[0].contentDocument.getElementById("click-map");
    };
};

function generateSelection(click_map)
{
    var click_map = JSON.parse(click_map.value);
    var res1 = click_map["res1"].split("-");
    var res2 = click_map["res2"].split("-");
    var selectSections =
    [
        {
            struct_asym_id: res1[0],
            start_residue_number: res1[2],
            end_residue_number: ++(res1[2]),
            color:
            {
                r: 0,
                g: 255,
                b: 0
            },
            sideChain: true,
            focus : true
        },
        {
            struct_asym_id: res2[0],
            start_residue_number: res2[2],
            end_residue_number: ++(res2[2]),
            color:
            {
                r: 255,
                g: 0,
                b: 0
            },
            sideChain: true,
            focus : true
        }
    ];
    return selectSections;
};