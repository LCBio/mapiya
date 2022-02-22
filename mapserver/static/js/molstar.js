function initMolStarViewer(viewport_id, project_id)
{
    var CurrentModel = getFirstModelNumber(project_id);
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
        viewerInstance.plugin.build().commit();
    }
    );    
    sessionStorage.setItem("model-loaded", CurrentModel);
    return viewerInstance;
};

function UpdateChainColourPairs(viewerInstance, applyColours = true)
{
    var colours_plotly = sessionStorage.getItem("chains-colors");
    if(sessionStorage.getItem("chains-colors") === null )
    {
        colours_plotly = sessionStorage.getItem("chains-colours-previous");
    }
    else
    {
        sessionStorage.setItem("chains-colours-previous", sessionStorage.getItem("chains-colors"));
    };
    var chains_colors = JSON.parse(colours_plotly);
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
    if(applyColours)
    {
        viewerInstance.plugin.managers.camera.reset();
        viewerInstance.visual.select(
        {
            data: selections
        });
    };
    sessionStorage.removeItem("chains-colors");
    return selections;
};

function HighlightClickMapData(viewerInstance)
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
            end_residue_number: parseInt(res1[2])+1,
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
            end_residue_number: parseInt(res2[2])+1,
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
    sessionStorage.removeItem("click-map");
    return selectSections;
};

function getFirstModelNumber(project_id)
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
    return CurrentModel;
}

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
    if(!(CurrentModel == ModelLoaded))
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
        sessionStorage.setItem("model-loaded", CurrentModel);
        viewerInstance.events.loadComplete.subscribe(() => 
        {
            viewerInstance.plugin.managers.structure.hierarchy.current.models[0].structures[0].cell.obj.data._props.label = `Model${CurrentModel}`;
            viewerInstance.plugin.build().commit();
        }
        );
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


async function add_representations(viewerInstance, type, alpha)
{
    const cell = viewerInstance.plugin.managers.structure.hierarchy.current.models[0].structures[0].cell;
    const components = 
    {
        polymer: await viewerInstance.plugin.builders.structure.tryCreateComponentStatic(cell, 'polymer'),
        ligand: await viewerInstance.plugin.builders.structure.tryCreateComponentStatic(cell, 'ligand'),
        water: await viewerInstance.plugin.builders.structure.tryCreateComponentStatic(cell, 'water')
    };
    const builder = viewerInstance.plugin.builders.structure.representation;
    const update = viewerInstance.plugin.build();
    if (components.polymer) 
    {
        builder.buildRepresentation(update, components.polymer, 
        { 
            type: type, 
            typeParams: 
            {
                alpha: alpha
            } 
        }, 
        { 
            tag: type
        }
        );
    }
    await update.commit();
    UpdateChainColourPairs(viewerInstance);
};

function UpdateColours1D(viewerInstance, applyColours = true)
{
    if(sessionStorage.getItem("colors_1d") === null )
    {
        UpdateChainColourPairs(viewerInstance);
        return [];
    }
    var colours_1d = JSON.parse(sessionStorage.getItem("colors_1d"));
    var x = colours_1d.x;
    var y = colours_1d.y;
    var selections_x = [];
    var selections_y = [];
    if(!(x == ""))
    {
        var chain_x = x[0].split("-")[1].split(':')[0];
        var entity_id_x = viewerInstance.plugin.managers.structure.hierarchy.current.models[0].structures[0].cell.obj.data.models[0].properties.structAsymMap.get(chain_x).entity_id;
        var residue_numbers = Array.from(viewerInstance.plugin.managers.structure.hierarchy.current.models[0].structures[0].cell.obj.data._props.models[0].sequence.sequences[entity_id_x-1].sequence.indexMap.keys());
        var j = x[1];
        for (var k in j)
        {
            var rgb = j[k].split('(')[1].split(')')[0].split(',');
            var current_resnum = residue_numbers[k];
            selections_x.push(
                {
                    struct_asym_id: chain_x,
                    start_residue_number: current_resnum,
                    end_residue_number: parseInt(current_resnum)+1,
                    color:
                    {
                        r: rgb[0],
                        g: rgb[1],
                        b: rgb[2]
                    },
                    sideChain: false,
                    focus : false
                }
            );
        };
    };
    if(!(y == ""))
    {
        var chain_y = y[0].split("-")[1].split(':')[0];
        var entity_id_y = viewerInstance.plugin.managers.structure.hierarchy.current.models[0].structures[0].cell.obj.data.models[0].properties.structAsymMap.get(chain_y).entity_id;
        var residue_numbers = Array.from(viewerInstance.plugin.managers.structure.hierarchy.current.models[0].structures[0].cell.obj.data._props.models[0].sequence.sequences[entity_id_y-1].sequence.indexMap.keys());
        var j = y[1];
        for (var k in j)
        {
            var rgb = j[k].split('(')[1].split(')')[0].split(',');
            var current_resnum = residue_numbers[k];
            selections_y.push(
                {
                    struct_asym_id: chain_y,
                    start_residue_number: current_resnum,
                    end_residue_number: parseInt(current_resnum)+1,
                    color:
                    {
                        r: rgb[0],
                        g: rgb[1],
                        b: rgb[2]
                    },
                    sideChain: false,
                    focus : false
                }
            );
        };
        
    };
    var selections = selections_x.concat(selections_y);
    if( (!(selections === null)) && applyColours)
    {
        viewerInstance.plugin.managers.camera.reset();
        viewerInstance.visual.select(
        {
            data: selections,
            nonSelectedColor:
            {
                r:255,
                g:255,
                b:255
            }
        }
        );
    };
    return selections;
};

function UpdateColoursContact(viewerInstance, applyColours = true)
{
    if(!(sessionStorage.getItem("active-colors") == 1)) return[];
    if(sessionStorage.getItem("colors_con") === null ) return [];
    var colours_contacts = JSON.parse(sessionStorage.getItem("colors_con"));
    
    var selections = [];
    if(colours_contacts == "")  return[];
    var chain1 = colours_contacts.objects.split(':')[0].split('-')[1];
    var chain2 = colours_contacts.objects.split(':')[1].split('-')[1];
    var contacts = colours_contacts.contacts;
    for (var i in contacts)
    {
        var res_data = i.split('-');
        var rgb = contacts[i].split('(')[1].split(')')[0].split(',');
        selections.push(
        {
            struct_asym_id: chain1,
            start_residue_number: res_data[0].split(':')[1],
            end_residue_number: parseInt(res_data[0].split(':')[1])+1,
            color:
            {
                r: rgb[0],
                g: rgb[1],
                b: rgb[2]
            },
            sideChain: false,
            focus : false
        },
        {
            struct_asym_id: chain2,
            start_residue_number: res_data[1].split(':')[1],
            end_residue_number: parseInt(res_data[1].split(':')[1])+1,
            color:
            {
                r: rgb[0],
                g: rgb[1],
                b: rgb[2]
            },
            sideChain: false,
            focus : false
        }
        );
    };
    if(applyColours)
    {
        viewerInstance.plugin.managers.camera.reset();
        viewerInstance.visual.select(
        {
            data: selections,
            nonSelectedColor:
            {
                r:255,
                g:255,
                b:255
            }
        });
    };
    return selections;
};

function process_events(viewerInstance,project_id)
{
    viewerInstance.events.loadComplete.subscribe(() => 
    {
        add_representations(viewerInstance, 'gaussian-surface', 0.15);
        UpdateChainColourPairs(viewerInstance);
    }
    );
    window.addEventListener('storage', e =>
    {
        var active_colours = parseInt(sessionStorage.getItem("active-colors"));
        switch (e.key)
        {
            case 'model-ix' :
                LoadCurrentModel(project_id,viewerInstance);
                break;
            case 'click-map' :
                HighlightClickMapData(viewerInstance);
                break;
            case 'active-colors':
                switch(active_colours)
                {
                    case 0:
                        UpdateChainColourPairs(viewerInstance);
                        break;
                    case 1:
                        UpdateColoursContact(viewerInstance);
                        break;
                    case 2:
                        UpdateColours1D(viewerInstance);
                        break;
                    default:
                        UpdateColoursContact(viewerInstance);
                        break;
                };
                break;
            case 'colors_con':
                switch(active_colours)
                {
                    case 1:
                        UpdateColoursContact(viewerInstance);
                        break;
                };
                break;
            case 'colors_1d':
                switch(active_colours)
                {
                    case 2:
                        UpdateColours1D(viewerInstance);
                        break;
                };
                break;
            
        };
    }
    );
};

function resetColours(viewerInstance)
{
    var selections = [];
    viewerInstance.visual.select(
    {
        data: selections,
        nonSelectedColor:
        {
            r:255,
            g:255,
            b:255
        }
    }
    );
};
