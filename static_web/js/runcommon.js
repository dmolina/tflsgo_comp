// register
Vue.filter('to_space', function (value) {
    return value.replace('_', ' ');
})

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
<div class="row">\
The required format is indicated&nbsp;<a v-bind:href="example">here</a>.\
</div>\
<div class="form-group row">\
<div class="col-md-3 col-lg-3 col-sm-12">\
<input id="alg_name" name="alg_name" class="form-control up" placeholder="Proposal">\
</div>\
<div class="col-md-6 col-lg-5 col-sm-12">\
<label id="file" for="fileupload" class="form-control no-border">Select a file (.csv or .xls) to upload<br/></label>\
</div>\
<div class="col-md-6 col-lg-4 col-sm-12">\
<input id="upload_button" type="file" class="col" name="file">\
</div>\
</div>\
</div>',
    props: ['benchmark'],
    computed: {
        example:  function(){
            var self = this;
            var example = self.benchmark.example;

            if (example.length > 0) {
                return "/static/examples/" +example +".xls";
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

var init_process = function() {
    console.log("init_process");
    $("i#refresh").removeClass("d-none");
    $("#submit_button").prop("disabled", true);
}

var finish_process = function() {
    console.log("finish_process");
    $("#submit_button").prop("disabled", false);
    $("i#refresh").addClass("d-none");
}

