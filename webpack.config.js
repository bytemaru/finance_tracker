const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
    mode: 'development',
    entry: './src/index.js',
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'dist'),
        clean: true
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './src/index.html' // будем хранить шаблон в src
        }),
    ],
    devServer: {
        static: './dist',
        port: 3000,
        open: true // автоматически откроет браузер
    },
};
