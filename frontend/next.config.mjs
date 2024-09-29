/** @type {import('next').NextConfig} */
const nextConfig = {
  sassOptions: {
    additionalData: `@import "styles/index.scss";`,
  }
};

export default nextConfig;
