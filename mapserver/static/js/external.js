

//---------------------------- External tools options --------------------------

// print selected dropdown value in a placeholder
function selectionChanged(element,obj) {
    document.getElementById(obj).innerHTML = element.value;
};


// generate 'protonation pH' when adding hydrogens
function return_pH_box() {
    var el = document.getElementById("atoms");
    if (el.value == 'all' || el.value == 'hydrogen') {
	if (document.getElementById("ph")) {
	    document.getElementById("ph-drop").style.cssText = "display: inline-block;";
	    document.getElementById("opt-ph").style.cssText = "color: gray;";
	    setTimeout(function() {document.getElementById("ph-drop").style.display = "none";}, 10000);
	} else {
	    var content = '<div class="opt-label col-lg-6" id="opt-ph">•&nbsp;&nbsp;protonation pH<span class="tooltiptext">Select pH to use for adding missing hydrogen atoms to the structure.<br>default: <i>7.0</i>\
                           <br><i>Notes</i><br>No extensive electrostatic analysis is performed; only default residue pKas are used.\
                           <br>Some residues can exist in multiple protonation states depending on specific pH.</span></div>\
                           <div class="dropdown"><input type="number" name="ph" id="ph" value="7.0" min="0.0" max="14.0" step="0.1" onchange="getVal(this);"><label for="ph"><i>range: 0-14</i></label></div>';
	    document.querySelector('#ph-drop').innerHTML = content;
	    document.getElementById("ph-drop").style.cssText = "display: inline-block;";
	    document.getElementById("opt-ph").style.cssText = "color: gray;";
	    setTimeout(function() {document.getElementById("ph-drop").style.display = "none";}, 10000);
	};
    } else {
	document.getElementById("ph-drop").style.display = "none";
    };
};


// generate 'max loop length' when adding missing residues
function return_res_gap() {
    var el = document.getElementById("resids");
    if (el.value != 'none') {
	if (document.getElementById("gap")) {
	    document.getElementById("res-gap").style.cssText = "display: inline-block;";
	    document.getElementById("opt-gap").style.cssText = "color: gray;";
	    setTimeout(function() {document.getElementById("res-gap").style.display = "none";}, 10000);
	} else {
	    var content = '<div class="opt-label col-lg-6" id="opt-gap">•&nbsp;&nbsp;max loop length<span class="tooltiptext">Select pH to use for adding missing hydrogen atoms to the structure.<br>default: <i>5</i>\
                           <br><i>Notes</i><br>No extensive electrostatic analysis is performed; only default residue pKas are used.\
                           <br>Some residues can exist in multiple protonation states depending on specific pH.</span></div>\
                           <div class="dropdown"><input type="number" name="gap" id="gap" value="5" min="1" max="200" step="1" onchange="getVal(this);"><label for="gap"><i>range: 1-200</i></label></div>';
	    document.querySelector('#res-gap').innerHTML = content;
	    document.getElementById("res-gap").style.cssText = "display: inline-block;";
	    document.getElementById("opt-gap").style.cssText = "color: gray;";
	    setTimeout(function() {document.getElementById("res-gap").style.display = "none";}, 10000);
	};
    } else {
	document.getElementById("res-gap").style.display = "none";
    };
};


// generate 'mutants' when substituting selected residues
function return_mutations() {
    var el = document.getElementById("mutations");
    if (el.value == 'true') {
	if (document.getElementById("mut")) {
	    document.getElementById("mutant").style.cssText = "display: inline-block;";
	    document.getElementById("opt-mut").style.cssText = "color: gray; vertical-align: super;";
	    setTimeout(function() {document.getElementById("mutant").style.display = "none";}, 30000);
	} else {
	    var content = '<div class="opt-label col-lg-6" id="opt-mut">•&nbsp;&nbsp;specify mutants<span class="tooltiptext">Select pH to use for adding missing hydrogen atoms to the structure.<br>default: <i>7.0</i>\
                           <br><i>Notes</i><br>No extensive electrostatic analysis is performed; only default residue pKas are used.\
                           <br>Some residues can exist in multiple protonation states depending on specific pH.</span></div>\
                           <div class="dropdown" id="opt-opt"><textarea id="mut" name="mut" rows="1" cols="20" placeholder="e.g., VAL-3-ILE:A, ILE-7-VAL:A"></textarea></div>';
	    document.querySelector('#mutant').innerHTML = content;
	    document.getElementById("mutant").style.cssText = "display: inline-block;";
	    document.getElementById("opt-mut").style.cssText = "color: gray; vertical-align: super;";
	    setTimeout(function() {document.getElementById("mutant").style.display = "none";}, 30000);
	};
    } else {
	document.getElementById("mutant").style.display = "none";
    };
};


// generate 'add environement' options
function return_envir() {
    var el = document.getElementById("envir");
    if (el.value == 'none') {
        document.getElementById("envir2").style.display = "none";
    } else {
	if ((document.getElementById("envir_box") && el.value == 'solvent') || (document.getElementById("lipid_box") && el.value == 'membrane')) {
	    document.getElementById("envir2").style.cssText = "display: inline-block;";
	    setTimeout(function() {document.getElementById("envir2").style.display = "none";}, 30000);
	} else {
	    ions = ['Na+', 'Cs+', 'K+', 'Li+', 'Rb+'];
	    positive = '';
	    ions.forEach(function (pos) {positive += '<option class="opt" value="' + pos + '">'+ pos +'</option>'});
	    ions = ['Cl-', 'Br-', 'F-', 'I-'];
	    negative = '';
	    ions.forEach(function (pos) {negative += '<option class="opt" value="' + pos + '">'+ pos +'</option>'});
	    var content = ''
	    if (el.value == 'solvent') {
		content += '<div class="opt-label col-lg-6 opt-env">•&nbsp;&nbsp;water box<span class="tooltiptext">Specify dimensions of water box.</span></div>'
		content += '<div class="dropdown"><select required class="dropbtn" id="envir_box"><option class="opt" value="unitcell">unitcell</option>\
                        <option class="opt" value="maxsize">max size</option><option class="opt" value="custom">custom</option></select></div>';
		content += '<div class="field-foldable" id="envir3" style="display:none;"></div>'
	    } else if (el.value == 'membrane') {
		var lipids = ['POPC', 'POPE', 'DLPC', 'DLPE', 'DMPC', 'DOPC', 'DPPC'];
		var lipid = '';
		lipids.forEach(function (pos) {lipid += '<option class="opt" value="' + pos + '">'+ pos +'</option>'});
		content += '<div class="opt-label col-lg-6 opt-env">•&nbsp;&nbsp;lipid type<span class="tooltiptext">Specify lipid type.</span></div>'
		content += '<div class="dropdown"><select required class="dropbtn" id="lipid_box">' + lipid + '</select></div>';
	    }
	    content += '<div class="opt-label col-lg-6 opt-env">•&nbsp;&nbsp;positive ion<span class="tooltiptext">Specify cation.</span></div>'
	    content += '<div class="dropdown"><select required class="dropbtn" id="pos_ion">' + positive + '</select></div>';
	    content += '<div class="opt-label col-lg-6 opt-env">•&nbsp;&nbsp;negative ion<span class="tooltiptext">Specify anion.</span></div>'
	    content += '<div class="dropdown"><select required class="dropbtn" id="neg_ion">' + negative + '</select></div>';

	    document.querySelector('#envir2').innerHTML = content;
	    document.getElementById("envir2").style.cssText = "display: inline-block;";
	    setTimeout(function() {document.getElementById("envir2").style.display = "none";}, 30000);
	};
    };
};


//---------- PDB CHAINS ----------

// derive available chain IDs from PDB file and create interactive buttons
var chains = ['A', 'B', 'C', 'D'];              /* replace the temporary array with the output from the initial PDB parsing */
var html = '';
chains.forEach(function (chain) {
    html += '<label class="chain-box"><input class="chain-input" id="ch_' + chain + '" value="' + chain + '" type="checkbox" checked><span class="chain-text">' + chain + '</span></label>';
});
document.querySelector('#chains').innerHTML = html;


// return a list of chains selected by the user
function return_chains() {
    selected = [];
    chains.forEach(function (chain) {
        if (document.getElementById("ch_"+chain).checked) {
            if (selected.includes(chain) == false) {
                selected.push(chain);
            };
        };
    });
    return selected;
};


//---------- FINAL VALUES FROM OPTIONS ----------

// assign selected value from dropdowns to a key in the 'opts' dictionary with options for external tools
var fixer = {};
var opts = {'ph':'7.0','atoms':'all','resids':'False','hetero':'all','nonstand':'True', 'dist':'8.0','ss':'stride','sa':'stride','hb':'edhb','elest':'apbs','rama':'stride', 'mutations':'false', 'envir_box':''};
function getVal(element) {
    opts[element.id] = element.value;
};

// pass selected_chains and opts (selected values of options) as inputs for external software
function submit_data() {
    selected_chains = return_chains()
    console.log(selected_chains, opts)            /* pass selected_chains and opts (selected values of options) as inputs for external software */
                                                        /* THEN: run PDBfixer and save PDB file in media */
                                                        /* THEN: show spinner when running in parallel: 1) STRIDE 2) EDHB 3) APBS and 4) calculate distance matrix */
                                                        /* THEN: display 'Your files' table with links to map & visualizer view */
};





//        test.addEventListener("mouseover", function( event ) {
//            event.target.style.color = "orange";
//	      setTimeout(function() {document.getElementById("ph-drop").style.display = "none";}, 5000);

//        }, false);
//        el.parentElement.style.width = "25%";