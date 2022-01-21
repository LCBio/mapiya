function initMolStarViewer(viewport_id, project_id)
{
    var CurrentModel = 0;
    if ( UrlExists(`/project/${project_id}/molstar/0`) )
    {
        CurrentModel = 0;
    }
    else if( UrlExists(`/project/${project_id}/molstar/1`) )
    {
        CurrentModel = 1;
    }
    var pdburl = `/project/${project_id}/molstar/${CurrentModel}`;
    var viewerInstance = new PDBeMolstarPlugin();
    var options =
    {
        customData:
        {
            url: pdburl ,
            format: 'pdb',
            binary: false
        },
        hideControls: true,
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
        expanded: true,
        selectInteraction: false
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
    viewerInstance.events.loadComplete.subscribe(() => 
    {
        viewerInstance.plugin.managers.structure.hierarchy.current.models[0].structures[0].cell.obj.data._props.label = `Model${CurrentModel}`;
    }
    );
    sessionStorage.setItem("model-loaded", CurrentModel);
    return viewerInstance;
};

function generateChainColourPairs()
{
    var colors_plotly = sessionStorage.getItem("chains-colors");
    if(sessionStorage.getItem("chains-colors") === null )
    {
        colors_plotly = sessionStorage.getItem("chains-colors-previous");
    }
    else
    {
        sessionStorage.setItem("chains-colors-previous", sessionStorage.getItem("chains-colors"));
    };
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
    sessionStorage.removeItem("chains-colors");
    return selections;
};

function updateMolStarViewer(viewerInstance)
{
    var selectSections = generateChainColourPairs().concat(PrepareClickMapData());
    viewerInstance.plugin.managers.camera.reset();
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

function PrepareClickMapData()
{
    if(sessionStorage.getItem("click-map") === null ) return [];
    var click_map = JSON.parse(sessionStorage.getItem("click-map"));
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
    sessionStorage.removeItem("click-map");
    return selectSections;
};

function getCurrentModelNumber()
{
    if(sessionStorage.getItem("model-ix") === null)
    {
        CurrentModel = 0;
    }
    else
    {
        CurrentModel = sessionStorage.getItem("model-ix");
    }
    return CurrentModel;
}

async function LoadCurrentModel(project_id, viewerInstance)
{   
    CurrentModel = getCurrentModelNumber();    
    var current_url = `/project/${project_id}/molstar/${CurrentModel}`;
    var ModelLoaded = sessionStorage.getItem("model-loaded");
    if(CurrentModel == ModelLoaded)
    {
        updateMolStarViewer(viewerInstance);
    }
    else
    {
        viewerInstance.clear();
        viewerInstance.visual.update(
        {
            customData:
            {
                url: current_url ,
                label : 'Model'+CurrentModel,
                format: 'pdb',
                binary: false
            },
            hideControls: true,
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
            expanded: true,
            selectInteraction: true,
            molstar_accessible_surface_area: true,
            loadCartoonsOnly: false,
            alphafoldView: false,
            visualStyle: 'cartoon'
        }
        );
        viewerInstance.events.loadComplete.subscribe(() => 
        {
            viewerInstance.plugin.managers.structure.hierarchy.current.models[0].structures[0].cell.obj.data._props.label = `Model${CurrentModel}`;
        }
        );
        updateMolStarViewer(viewerInstance);
        sessionStorage.setItem("model-loaded", CurrentModel);
    };
};

function UrlExists(url)
{
    var request = new XMLHttpRequest();
    request.open('HEAD', url, false);
    request.send();
    if (request.status != 404)
        return true;
    else
        return false;
};