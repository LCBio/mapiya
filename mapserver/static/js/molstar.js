let initMolStarViewer = function (pdburl, viewport_id) {
    let viewerInstance = new PDBeMolstarPlugin();
    let options = {
        customData: { url: pdburl , format: 'pdb', binary: false },
        hideControls: true,
        bgColor: {r:255, g:255, b:255},
        pdbeLink: false,
        landscape: true,
        hideStructure: ['het', 'water', 'carbs', 'nonStandard', 'coarse']
    }
    let viewerContainer = document.getElementById(viewport_id);
    viewerInstance.render(viewerContainer, options);
};
