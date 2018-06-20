var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  mode: 'development',
  entry: './assets/src/app/main.js',
  output: {
    path: path.resolve(__dirname, './assets/dist/bundles'),
    filename: "[name]-[hash].js",
    publicPath: '/static/dist/bundles/',
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          'vue-style-loader',
          'css-loader'
        ],
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: {
          loaders: {
            'scss': 'vue-style-loader!css-loader!sass-loader',
            'sass': 'vue-style-loader!css-loader!sass-loader?indentedSyntax'
          // other vue-loader options go here
          }
        }
      },
      // {
      //   test: /\.js$/,
      //   loader: 'babel-loader',
      //   exclude: /node_modules/
      // },
      {
        test: /\.(png|jpg|gif|svg)$/,
        loader: 'file-loader',
        options: {
          name: '[name].[ext]?[hash]'
        }
      }
    ]
  },
  resolve: {
    alias: {
      'vue$': 'vue/dist/vue.esm.js'
    }
  },
  // devServer: {
  //   historyApiFallback: true,
  //   noInfo: true
  // },
  // performance: {
  //   hints: false
  // },
  // devtool: '#eval-source-map'
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'})
  ]
}

// if (process.env.NODE_ENV === 'production') {
//   module.exports.devtool = '#source-map'
//   // http://vue-loader.vuejs.org/en/workflow/production.html
//   module.exports.plugins = (module.exports.plugins || []).concat([
//     new webpack.DefinePlugin({
//       'process.env': {
//         NODE_ENV: '"production"'
//       }
//     }),
//     new webpack.optimize.UglifyJsPlugin({
//       sourceMap: true,
//       compress: {
//         warnings: false
//       }
//     }),
//     new webpack.LoaderOptionsPlugin({
//       minimize: true
//     })
//   ])
// }
