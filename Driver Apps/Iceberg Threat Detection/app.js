var app = angular.module('app', []);
app.controller('ctrl', function($scope) {
	$scope.dia = 0;
	$scope.dep = 0;
    $scope.vol = function() {
        var vol = Math.PI * Math.pow($scope.dia / 2, 2) * ($scope.dep / 3);
        return vol.toFixed(1);
    }
});