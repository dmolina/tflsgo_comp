Vue.component('select-bench', {
    template: '<div><label>Select the Benchmark </label><select v-model="selected" v-on:change="changed">\
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

            if (self.selected < 0) {
                this.$emit('update:benchmark', {});
            }
            else {
                var bench = self.benchmarks[self.selected];
                this.$emit('update:benchmark', bench);
            }
        }
    }
});


Vue.component('input-alg', {
    template: '<div>\
The required format is indicated <a v-bind:href="example">here</a>.\
</p>\
<label id="file" for="fileupload">Select a file (.csv or .xls) to upload<br/></label>\
<p><input id="upload_button" type="file" name="file"></p>\
</div>',
    props: ['benchmark'],
    computed: {
        example:  function(){
            var self = this;
            var example = self.benchmark.example;

            if (example.length > 0) {
                return "examples/" +example +".xls";
            }
            else {
                return '#'
            }

        }
    }
}
);

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
