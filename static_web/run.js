var app = new Vue({
    el: '#app',
    data: {
        benchmarks: {}
    }
    mounted: function() {
        val self = this;
        $.ajax({
            url: 'http://localhost:5000/benchmarks',
            method: 'GET',
            success: function(data) {
                self.benchmarks = data['benchmarks'];
            }
        })
    }
})
