var app = angular.module('app', []);
app.controller('ctrl', function($scope) {
	$scope.dia = 0;
	$scope.dep = 0;
	$scope.keel = 0;
	$scope.lat = 0;
	$scope.lon = 0;
	$scope.head = 0;
    $scope.vol = function() {
        var vol = Math.PI * Math.pow($scope.dia / 2, 2) * ($scope.dep / 3);
        return vol.toFixed(1);
    }
});
var canvas = document.getElementById("image");
var drawing = canvas.getContext("2d");
var img = document.getElementById("map");
drawing.drawImage(img, 0, 0);
drawing.moveTo(0, 0);
drawing.lineTo(195, 259);
drawing.moveTo(195, 0);
drawing.lineTo(0, 259);
drawing.lineWidth = 5;
drawing.stroke();