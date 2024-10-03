import { Link } from "@nextui-org/link";

import { Navbar } from "@/components/navbar";
import {
  GithubIcon,
} from "@/components/icons";

export default function DefaultLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex flex-col h-screen">
      <Navbar />
      <main className="container flex-grow px-6 pt-16 mx-auto max-w-7xl">
        {children}
      </main>
      <footer className="flex items-center justify-center w-full py-3">
        <Link
          isExternal
          className="flex items-center gap-1 text-current"
          href="https://github.com/ngtruongthanh98"
          title="personal github homepage"
        >
          <span className="text-default-600">Developed by</span>
          <p className="flex items-center space-x-2 text-lg font-semibold text-primary">
            ngtruongthanh98
            <span className="ml-1 text-default-500">
              <GithubIcon className="w-5 h-5" />
            </span>
          </p>
        </Link>
      </footer>
    </div>
  );
}
