function debug (s) {
    $("#debug").append(s + "<br>");
}

GREEN = 0;
YELLOW = 1;
RED = 2;

locs = {"hibernia":  {"lat": 46.7504, "lon": 48.7819, "depth": 78 },
        "searose":   {"lat": 46.7895, "lon": 48.1417, "depth": 107},
        "terranova": {"lat": 46.4000, "lon": 48.4000, "depth": 91 },
        "hebron":    {"lat": 46.5440, "lon": 48.4980, "depth": 93 }};


function getVolume(dia, height) {
    return 1/3 * Math.PI * Math.pow(dia / 2, 2) * height;
}


function updateVolume(dia, height) {
    var dia = $("#dia").val();
    var height = $("#height").val();

    if (isNaN(dia) || isNaN(height) || dia == "" || height == "") return;

    var volume = getVolume(dia, height).toFixed(2);

    $("#volume").html(volume + " cm<sup>3</sup>");
}



// distance between two points in nautical miles
function getDist(lat1, lon1, lat2, lon2) {
    var latNM = (lat2 - lat1) * 60;
    var lonNM = (lon2 - lon1) * 41.45;
    return Math.sqrt(latNM * latNM + lonNM * lonNM);
}

// heading is degrees clockwise from north
function closestApproach(latIce, lonIce, latBase, lonBase, heading) {
    var relLat = (latBase - latIce) * 60;
    var relLon = -(lonBase - lonIce) * 41.45;
    var radHeading = heading * Math.PI / 180;

    var closestX = Math.cos(radHeading) * relLon - Math.sin(radHeading) * relLat;
    var closestY = Math.sin(radHeading) * relLon + Math.cos(radHeading) * relLat;

    if (closestY >= 0) {
        return Math.abs(closestX);
    }
    return getDist(latIce, lonIce, latBase, lonBase);
}

function setThreatLevel(id, level) {
    if (level == 0) {
        $("#" + id).html("<span style='font-weight:bold; color:green'>GREEN</span>");
    } else if (level == 1) {
        $("#" + id).html("<span style='font-weight:bold; color:rgb(220,220,0)'>YELLOW</span>");
    } else if (level == 2) {
        $("#" + id).html("<span style='font-weight:bold; color:red'>RED</span>");
    } else {
        $("#" + id).html("UNKNOWN");
    }
}

function updateThreat(name, latIce, lonIce, depthIce, heading) {
    var latBase = locs[name].lat;
    var lonBase = locs[name].lon;
    var depthBase = locs[name].depth;

    closest = closestApproach(latIce, lonIce, latBase, lonBase, heading);

    if (closest > 10 || depthIce >= 1.1 * depthBase) {
        setThreatLevel(name + "_sur", 0);
    } else if (closest > 5) {
        setThreatLevel(name + "_sur", 1);
    } else {
        setThreatLevel(name + "_sur", 2);
    }

    if (depthIce >= 1.1 * depthBase || depthIce < .7 * depthBase) {
        setThreatLevel(name + "_sub", 0);
    } else if (depthIce >= .7 * depthBase && depthIce <= .9 * depthBase) {
        setThreatLevel(name + "_sub", 1);
    } else {
        setThreatLevel(name + "_sub", 2);
    }
}

function updateThreats() {
    var depth = Math.abs($("#depth").val());
    var lat = $("#lat").val();
    var lon = Math.abs($("#lon").val());
    var heading = $("#heading").val();

    if (isNaN(depth) || isNaN(lat) || isNaN(lon) || isNaN(heading) ||
        depth == "" || lat == "" || lon == "" || heading == "") return;

    updateThreat("hibernia", lat, lon, depth, heading);
    updateThreat("searose", lat, lon, depth, heading);
    updateThreat("terranova", lat, lon, depth, heading);
    updateThreat("hebron", lat, lon, depth, heading);
}


$(function() {
    $("#dia").change(updateVolume);
    $("#height").change(updateVolume);

    $("#depth").change(updateThreats);
    $("#lat").change(updateThreats);
    $("#lon").change(updateThreats);
    $("#heading").change(updateThreats);
}); 