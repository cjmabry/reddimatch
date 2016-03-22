var gulp = require('gulp'),
    browserSync = require('browser-sync'),
    uglify = require('gulp-uglify'),
    imagemin = require('gulp-imagemin'),
    cache = require('gulp-cache'),
    del = require('del'),
    runSequence = require('run-sequence'),
    minifyCss = require('gulp-minify-css'),
    useref = require('gulp-useref'),
    gulpIf = require('gulp-if');

var exec = require('child_process').exec;

// Run python server
gulp.task('runserver', function() {
  var proc = exec('python run.py');
});

// browserSync
gulp.task('browserSync', function() {
  browserSync.init({
    notify: false,
    proxy: "127.0.0.1:8000"
  });
});

// Watchers
gulp.task('watch', function() {
  // gulp.watch('app/scss/**/*.scss', ['sass']);
  gulp.watch('app/*.html', browserSync.reload);
  gulp.watch('app/static/js/**/*.js', browserSync.reload);
});

// Optimization Tasks

// JS
gulp.task('uglify', function() {
  return gulp.src('app/static/js/**/*.js')
    .pipe(uglify())
    .pipe(gulp.dest('dist/app/static/js'));
});

// CSS
gulp.task('minify-css', function() {
  return gulp.src('app/static/css/*.css')
    .pipe(minifyCss({compatibility: 'ie8'}))
    .pipe(gulp.dest('dist/app/static/css'));
});

// Images
gulp.task('imagemin', function(){
  return gulp.src('app/static/images/**/*.+(png|jpg|gif|svg)')
  .pipe(cache(imagemin()))
  .pipe(gulp.dest('dist/app/static/images'));
});

// Copy HTML
gulp.task('html', function() {
  return gulp.src('app/templates/*.html')
  .pipe(gulp.dest('dist/app/templates'));
});

// Copy Python
gulp.task('python', function() {
  return gulp.src('app/*.py')
  .pipe(gulp.dest('dist/app'));
});

// Copy Fonts
gulp.task('fonts', function() {
  return gulp.src('app/static/fonts/**/*')
  .pipe(gulp.dest('dist/app/static/fonts'));
});

// Cleaning
gulp.task('clean:dist', function() {
  return del.sync('dist');
});


// Build Sequences
gulp.task('default', function(callback) {
  runSequence(['runserver', 'browserSync', 'watch'],
    callback
  );
});

gulp.task('build', function(callback) {
  runSequence(
    'clean:dist',
    [ 'python','html','minify-css','uglify','imagemin', 'fonts'],
    callback
  );
});
