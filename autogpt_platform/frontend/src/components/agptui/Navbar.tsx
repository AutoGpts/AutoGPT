import * as React from "react";
import Link from "next/link";
import { ProfilePopoutMenu } from "./ProfilePopoutMenu";
import { IconType, IconLogIn } from "@/components/ui/icons";
import { MobileNavBar } from "./MobileNavBar";
import { Button } from "./Button";
import CreditsCard from "./CreditsCard";
import { ProfileDetails } from "@/lib/autogpt-server-api/types";
import { User } from "@supabase/supabase-js";
import AutoGPTServerAPIServerSide from "@/lib/autogpt-server-api/clientServer";

interface NavLink {
  name: string;
  href: string;
}

interface NavbarProps {
  user: User | null;
  isLoggedIn: boolean;
  links: NavLink[];
  activeLink: string;
  menuItemGroups: {
    groupName?: string;
    items: {
      icon: IconType;
      text: string;
      href?: string;
      onClick?: () => void;
    }[];
  }[];
}

async function getProfileData(user: User | null) {
  console.log(user);
  const api = new AutoGPTServerAPIServerSide();
  const [profile, credits] = await Promise.all([
    api.getStoreProfile(),
    api.getUserCredit(),
  ]);

  return {
    profile,
    credits,
  };
}
export const Navbar = async ({
  user,
  isLoggedIn,
  links,
  activeLink,
  menuItemGroups,
}: NavbarProps) => {
  let profile: ProfileDetails | null = null;
  let credits: { credits: number } = { credits: 0 };
  if (isLoggedIn) {
    console.log("Fetching profile data");
    console.log(user);
    const { profile: t_profile, credits: t_credits } =
      await getProfileData(user);
    profile = t_profile;
    credits = t_credits;
  }

  return (
    <>
      <nav className="sticky top-0 hidden h-20 w-[1408px] items-center justify-between rounded-bl-2xl rounded-br-2xl border border-white/50 bg-white/5 py-3 pl-6 pr-3 backdrop-blur-[26px] md:inline-flex">
        <div className="flex items-center space-x-10">
          {links.map((link) => (
            <div key={link.name} className="relative">
              <Link href={link.href}>
                <div
                  className={`text-[${activeLink === link.href ? "#272727" : "#474747"}] font-neue text-2xl font-medium leading-9 tracking-tight`}
                >
                  {link.name}
                </div>
              </Link>
              {activeLink === link.href && (
                <div className="absolute bottom-[-30px] left-[-10px] h-1.5 w-full bg-[#282828]" />
              )}
            </div>
          ))}
        </div>
        {/* Profile section */}
        {isLoggedIn ? (
          <div className="flex items-center gap-4">
            {profile && <CreditsCard credits={credits.credits} />}
            <ProfilePopoutMenu
              menuItemGroups={menuItemGroups}
              userName={profile?.username}
              userEmail={profile?.name}
              avatarSrc={profile?.avatar_url}
            />
          </div>
        ) : (
          <Link href="/login">
            <Button
              variant="default"
              size="sm"
              className="flex items-center justify-end space-x-2"
            >
              <IconLogIn className="h-5 w-5" />
              <span>Log In</span>
            </Button>
          </Link>
        )}
      </nav>
      {/* Mobile Navbar - Adjust positioning */}
      <>
        {isLoggedIn ? (
          <div className="fixed right-4 top-4 z-50">
            <MobileNavBar
              userName={profile?.username}
              activeLink={activeLink}
              menuItemGroups={[
                {
                  groupName: "Navigation",
                  items: links.map((link) => ({
                    icon:
                      link.name === "Agent Store"
                        ? IconType.Marketplace
                        : link.name === "Library"
                          ? IconType.Library
                          : link.name === "Build"
                            ? IconType.Builder
                            : IconType.LayoutDashboard,
                    text: link.name,
                    href: link.href,
                  })),
                },
                ...menuItemGroups,
              ]}
              userEmail={profile?.name}
              avatarSrc={profile?.avatar_url}
            />
          </div>
        ) : (
          <Link
            href="/login"
            className="fixed right-4 top-4 z-50 mt-4 inline-flex h-8 items-center justify-end rounded-lg pr-4 md:hidden"
          >
            <Button
              variant="default"
              size="sm"
              className="flex items-center space-x-2"
            >
              <IconLogIn className="h-5 w-5" />
              <span>Log In</span>
            </Button>
          </Link>
        )}
      </>
    </>
  );
};
