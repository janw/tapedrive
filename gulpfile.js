var gulp         = require("gulp"),
    autoprefixer = require("gulp-autoprefixer"),
    babel        = require('gulp-babel'),
    concat       = require('gulp-concat'),
    rename       = require('gulp-rename'),
    sass         = require("gulp-sass"),
    uglify       = require('gulp-uglify'),
    gutil        = require('gulp-util');


var src_dir = "./assets/src"
var dist_dir = "./assets/dist"

var scss_src = src_dir+"/scss/**/*.scss"
var scss_dest = dist_dir+"/css"

var js_src = src_dir+"/js/*.js"
var js_dest = dist_dir+"/js"

function logError (err) {
    gutil.log(gutil.colors.red('[Error]'), err.toString());
}

gulp.task("scss", function () {
    gulp.src(scss_src, { sourcemaps: true })
        .pipe(sass({
            outputStyle : "compressed",
            precision: 8,
            includePaths: ['node_modules/bootstrap/scss'],
        }))
        .pipe(autoprefixer({
            browsers : ["last 2 versions"]
        }))
        .pipe(gulp.dest(scss_dest))
});

gulp.task("basejs", function () {
    gulp.src([
            './node_modules/jquery/dist/jquery.js',
            './node_modules/popper.js/dist/umd/popper.js',
            './node_modules/bootstrap/dist/js/bootstrap.js',
            './node_modules/jsrender/jsrender.js',
            js_src,
        ],  { sourcemaps: true })
        .pipe(concat('base.js'))
        .pipe(gulp.dest(js_dest))
        .pipe(rename('base.min.js'))
        .pipe(uglify())
        .on('error', logError)
        .pipe(gulp.dest(js_dest));
});


// Watch asset folder for changes
gulp.task("watch", ["scss", "basejs"], function () {
    var scss_watcher = gulp.watch(scss_src, ["scss"])
        .on('error', logError);
    var basejs_watcher = gulp.watch(js_src, ["basejs"])
        .on('error', logError);
})

// Set watch as default task
gulp.task("default", ["watch"])

// Set watch as default task
gulp.task("build", ["scss", "basejs"])
