import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import "./globals.css";
import React from "react";
import SideNav from "@/components/sidenav/sidenav";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}): JSX.Element {
  return (
    <html lang="en">
      <head/>
      <body className={"d-flex vh-100"}>
        <SideNav />
        <main className={"w-100 vh-100 overflow-auto"}>
          {children}
        </main>
      </body>
    </html>
  );
}
