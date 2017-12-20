var app = new Vue({
    el: '#app',
    data: {
        benchmarks: {},
        selected: '',
        algs: {},
        sel_algs: [],
        error: ''
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
            $.ajax({
                url: 'http://localhost:5000/algs/' +self.selected,
                method: 'GET',
                sucess: function(data) {
                    self.algs = data['algs'];
                    self.error = data['error'];
                }
            });
        }

    }

})
