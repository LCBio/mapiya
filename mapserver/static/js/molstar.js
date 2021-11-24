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

class getClickMapFromPlotly
{
    constructor()
    {
        this.click_map = document.getElementsByTagName("iframe")[0].contentDocument.getElementById("click-map");
    };
};

async function delay(time) 
{
    return new Promise(resolve => setTimeout(resolve, time));
}


async function generateChainColourPairs()
{

    await delay(10000);
    var colors_plotly = document.getElementsByTagName("iframe")[0].contentDocument.getElementById("chains-colors");
    var chains_colors = JSON.parse(colors_plotly.value);
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


function checkIframeLoaded(viewerInstance)
{
    var iframe = document.getElementsByTagName("iframe")[0];
    var iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

    // Check if loading is complete
    if (  iframeDoc.readyState  == 'complete' )
    {
        return true;
    } 
    return false;
};

class getSessionStorageVariables
{
    constructor()
    {
        this.struct_asym_id = sessionStorage.getItem('struct_asym_id');
        this.first_residue_number = sessionStorage.getItem('first_residue_number');
        this.second_residue_number = sessionStorage.getItem('second_residue_number');
        this.color_r = sessionStorage.getItem('color_r');
        this.color_g = sessionStorage.getItem('color_g');
        this.color_b = sessionStorage.getItem('color_b');
    }
};


function setSessionStorageVariables (
    struct_asym_id,
    first_residue_number,
    second_residue_number,
    color_r,
    color_g,
    color_b
    )
{
    sessionStorage.setItem('struct_asym_id', struct_asym_id);
    sessionStorage.setItem('first_residue_number', first_residue_number);
    sessionStorage.setItem('second_residue_number', second_residue_number);
    sessionStorage.setItem('color_r', color_r);
    sessionStorage.setItem('color_g', color_g);
    sessionStorage.setItem('color_b', color_b);
};

function setSessionStorageVariablesChainColours(
    struct_asym_id,
    chains_color_r,
    chains_color_g,
    chains_color_b,
    chains_color_a
)
{
    sessionStorage.setItem('struct_asym_id', struct_asym_id);
    sessionStorage.setItem('chains_color_r', chains_colors_r);
    sessionStorage.setItem('chains_color_r', chains_colors_r);
    sessionStorage.setItem('chains_color_r', chains_colors_r);
    sessionStorage.setItem('chains_color_r', chains_colors_r);


};