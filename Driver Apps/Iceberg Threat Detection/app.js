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
        var ctx = this.getContext("2d");
        var img = $("#map")[0];
        ctx.clearRect(0, 0, this.width, this.height);
        ctx.drawImage(img, 0, 0);
        ctx.rect(getLatitude() - 1, getLongitude() - 1, 3, 3);
        ctx.fillStyle = 'red';
        ctx.fill();
    })

    $("#clr").click(function(){
        var c = $("canvas#image")[0];
        var ctx = c.getContext("2d");
        var img = $("#map")[0];
        ctx.clearRect(0, 0, c.width, c.height);
    })

    function getLatitude() {
        return $("#latitude").val();
    }

    function getLongitude() {
        return $("#longitude").val();
    }
})