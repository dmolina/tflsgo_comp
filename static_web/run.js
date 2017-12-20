var app = new Vue({
    el: '#app',
    data: {
        benchmarks: {},
        selected: '',
        available_algs: {},
        algs: [],
        error: '',
        dimension: ''
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
    },
    methods: {
        onChangedBenchmark: function() {
            var self = this;
            var dimensions = self.benchmarks[self.selected].dimensions;

            if (length(dimensions)==1) {
                self.dimension = dimensions[0];
            }
            $.ajax({
                url: 'http://localhost:5000/algs/' +self.selected,
                method: 'GET',
                sucess: function(data) {
                    self.available_algs = data['algs'];
                    self.error = data['error'];
                }
            });
        }

    }

})
