var app = angular.module('app', []);

app.controller('ctrl', function($scope) {
    $scope.dia = 0;
    $scope.dep = 0;
    $scope.keel = 0;
    $scope.lat = 0;
    $scope.lon = 0;
    $scope.head = 0;

    $scope.vol = function() {
        if ($scope.dia != 0 && $scope.dep != 0) {
            var vol = Math.PI * Math.pow($scope.dia / 2, 2) * ($scope.dep / 3);
            return vol.toFixed(1);
        } else {
            return "Unknown";
        }
    }

    function surface(depth) {
        if ($scope.keel != 0 && $scope.lat != 0 && $scope.lon != 0) {
            if ($scope.keel <= depth * 1.1) {
                return "Green";
            } else {
                return "Red";
            }
        } else {
            return "Unknown";
        }
    }

    function subsea(depth) {
        if ($scope.keel != 0 && $scope.lat != 0 && $scope.lon != 0) {
            if ($scope.keel <= depth * 1.1 || $scope.keel > depth * 0.7) {
                return "Green";
            } else if ($scope.keel > depth * 0.9 && $scope.keel <= depth * 0.7) {
                return "Yellow";
            } else {
                return "Red";
            }
        } else {
            return "Unknown";
        }
    }

    $scope.hibsur = function() { return surface(-78); }

    $scope.hibsub = function() { return subsea(-78); }

    $scope.seasur = function() { return surface(-107); }

    $scope.seasub = function() { return subsea(-107); }

    $scope.tersur = function() { return surface(-91); }

    $scope.tersub = function() { return subsea(-91); }

    $scope.hebsur = function() { return surface(-93); }

    $scope.hebsub = function() { return subsea(-93); }
});

$(document).ready(function(){
    var c = document.getElementById("image");
    var ctx = c.getContext("2d");
    var img = document.getElementById("map");
    ctx.drawImage(img, 0, 0);

    $("#image").click(function(){
        ctx.clearRect(0, 0, this.width, this.height);
        ctx.drawImage(img, 0, 0);
        ctx.fillStyle = 'red';
        ctx.fillRect(getLongitude() - 1, getLatitude() - 1, 3, 3);
    })

    function getLatitude() {
        //return $("#latitude").val();
        var lat = $("#latitude").val();
        var distance = Math.round(Math.abs(Number(lat) - 48.09) * 142.936288);
        console.log(distance);
        return distance;
    }

    function getLongitude() {
        //return $("#longitude").val();
        var lon = $("#longitude").val();
        console.log(lon);
        var distance = Math.round(Math.abs(Number(lon) + 49.634) * 96.758105);
        console.log(distance);
        return distance;
    }
})