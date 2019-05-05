var gulp = require('gulp');
var sass = require("gulp-sass");
var concat = require("gulp-concat");

var src_dir = "./assets/src",
    dist_dir = "./assets/dist",
    scss_src = src_dir + "/scss/**/*.scss",
    scss_dest = dist_dir + "/css",
    app_src = src_dir + "/app/main.js",
    js_src = src_dir + "/js/*.js",
    js_dest = dist_dir + "/js";


function compileCss() {
    return gulp.src(scss_src)
        .pipe(sass({
            outputStyle: "compressed",
            precision: 8,
            includePaths: ['node_modules/bootstrap/scss'],
        }).on('error', sass.logError))
        .pipe(gulp.dest(scss_dest));
}

function legacyJs() {
    return gulp.src([
        './node_modules/jquery/dist/jquery.js',
        './node_modules/popper.js/dist/umd/popper.js',
        './node_modules/bootstrap/dist/js/bootstrap.js',
        './node_modules/jsrender/jsrender.js',
        './node_modules/holderjs/holder.js',
        js_src,
    ], { sourcemaps: true })
        .pipe(concat("legacy.js"))
        .pipe(gulp.dest(js_dest));
}

function watchChanges() {
    gulp.watch(scss_src, compileCss);
    gulp.watch(js_src, legacyJs);
}

exports.sass = compileCss
exports.default = compileCss
exports.watch = watchChanges
exports.legacyjs = legacyJs
exports.dev = gulp.series(gulp.parallel(compileCss, legacyJs), watchChanges)
