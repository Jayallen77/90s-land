import sharp from 'sharp';
const [input,output]=process.argv.slice(2);
await sharp(input).png({compressionLevel:9,adaptiveFiltering:false}).toFile(output);
