var app = new Vue({
    el: '#app',
    data: {
        benchmarks: [],
        selected: '',
        message: 'hola'
    },
    mounted: function() {
        var self = this;
        $.ajax({
            url: 'http://localhost:5000/benchmarks',
            method: 'GET',
            success: function(data) {
                self.benchmarks = data['benchmarks'];
            }
        })
    }
})
