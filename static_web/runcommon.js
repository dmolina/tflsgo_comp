Vue.component('select-bench', {
    template: '<select v-model="selected" v-on:change="changed">\
        <option value="" selected="selected" value="-1">------</option>\
        <option v-for="bench in benchmarks" :value="bench.id">{{bench.name}}</option>\
        </select>',
    props: {'benchmark': { type: Object },
            'token': {
                type: String,
                default: function() { return ''; }
    }},
    data: function() {
        return {'benchmarks': [], 'selected': -1}
    },
    mounted: function() {
        var self = this;
        var token = self.token;

        if (token) {
            token = '/' +token;
        }

        $.ajax({
            url: '/benchmarks' +token,
            method: 'GET',
        }).done(function(data) {
            self.benchmarks = data['benchmarks'];
        });
 
    },
    methods: {
        changed: function() {
            var self = this;
            var bench = {}

            if (self.selected >= 0) {
                var bench = self.benchmarks[self.selected];
            }

            this.$emit('update:benchmark', bench);
            this.$emit('updated', bench);
        }
    }
});


Vue.component('input-alg', {
    template: '<div>\
The required format is indicated <a v-bind:href="example">here</a>.\
</p>\
<label id="file" for="fileupload">Select a file (.csv or .xls) to upload<br/></label>\
<p><input id="upload_button" type="file" name="file"></p>\
<input id="alg_name" name="alg_name" placeholder="Proposal">\
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

var make_ajax_noform = function(name, data) {

    return {url: '/' +name,
            type: 'POST',
            data: data,
            dataType: 'json',
            cache: false,
            contentType: false,
            processData: false
           };
}

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

var process_fail = function(data) {
    var error = data.responseJSON['message'];
    var result = '';

    for (name in error) {
        result += name +': ' +error[name];
    }
    return result;
}
