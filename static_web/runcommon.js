Vue.component('select-bench', {
    template: '<div><label>Benchmark</label><select v-model="selected" v-on:change="changed">\
        <option value="" selected="selected" value="-1">------</option>\
        <option v-for="bench in benchmarks" :value="bench.id">{{bench.name}}</option>\
        </select></div>',
    props: ['benchmark'],
    data: function() {
        return {'benchmarks': [], 'selected': -1}
    },
    mounted: function() {
        var self = this;
        $.ajax({
            url: '/benchmarks',
            method: 'GET',
            success: function(data) {
                self.benchmarks = data['benchmarks'];
            }
        });
    },
    methods: {
        changed: function() {
            var self = this;
            var bench = self.benchmarks[self.selected];
            this.$emit('update:benchmark', bench);
            console.log(self.benchmark);
        }
    }
});

var make_ajax_info = function(name, e) {
    e.preventDefault();
    var formData = new FormData(e.target);

    return {url: '/' +name,
            type: 'POST',
            data: formData,
            dataType: 'json',
            cache: false,
            contentType: false,
            processData: false
    };
}
