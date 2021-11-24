function initMolStarViewer(pdburl, viewport_id)
{
    var viewerInstance = new PDBeMolstarPlugin();
    var options =
    {
        customData: { url: pdburl , format: 'pdb', binary: false },
        hideControls: true,
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

    }
    var viewerContainer = document.getElementById(viewport_id);
    viewerInstance.render(viewerContainer, options);
    return viewerInstance;
}
