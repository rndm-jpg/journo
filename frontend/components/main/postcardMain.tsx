"use client";

import React from "react";
import Link from "next/link";

interface PostcardMainProps {
  children: React.ReactNode,
  title: string,
  headtitle?: string,
  headurl?: string,
  foottitle?: string,
  footurl?: string,
  backbutton?: boolean
}

export default function PostcardMain({
  backbutton,
  children,
  title,
  headtitle,
  headurl,
  foottitle,
  footurl,
}: PostcardMainProps): JSX.Element {
  return (
    <div className={"pb-3"}>
      <div className="top-0 position-sticky bg-white py-3 border-bottom mb-3 lh-1" style={{
        zIndex: 1000,
      }}>
        {backbutton &&
          <p className={"text-primary container mb-0 a"} style={{cursor: "pointer"}} onClick={() => window.history.back()}>
            back
          </p>
        }
        {!backbutton && headtitle &&
          <>
            {headurl &&
              <Link href={headurl} className={"text-primary container"}>
                {headtitle}
              </Link>
            }
            {!headurl &&
              <div className={"container"}>
                {headtitle}
              </div>
            }
          </>
        }
        <h1 className="container h3 mb-0">
          {title}
        </h1>
        {foottitle &&
          <>
            {footurl &&
              <Link href={footurl} className={"text-primary container"}>
                {foottitle}
              </Link>
            }
            {!footurl &&
              <div className={"container text-secondary"}>
                {foottitle}
              </div>
            }
          </>
        }
      </div>
      <div className="container">
        {children}
      </div>
    </div>
  );
}