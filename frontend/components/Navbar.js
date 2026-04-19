"use client";

import Image from "next/image";

export default function Navbar({ title = "Workspace" }) {
  return (
    <header className="flex justify-between items-center w-full px-8 py-4 sticky top-0 z-40 bg-white/70 backdrop-blur-xl shadow-sm bg-emerald-50/50 dark:bg-emerald-900/20">
      <div className="flex items-center gap-6 flex-1">
        <h2 className="text-xl font-black text-emerald-900 dark:text-emerald-50 tracking-tight">{title}</h2>
        <div className="relative w-full max-w-md hidden md:block">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm">search</span>
          <input className="w-full pl-10 pr-4 py-2 bg-surface-container-lowest rounded-full border-none focus:ring-2 focus:ring-primary-container text-sm" placeholder="Search funds or analysis..." type="text"/>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="p-2 rounded-full hover:bg-emerald-100/50 transition-colors text-on-surface-variant">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <button className="p-2 rounded-full hover:bg-emerald-100/50 transition-colors text-on-surface-variant">
          <span className="material-symbols-outlined">settings</span>
        </button>
        <div className="w-10 h-10 rounded-full overflow-hidden ml-2 border-2 border-primary-container/30">
          <Image 
            alt="User profile" 
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuAfn1WS8F9x1VXkEzQL7g8AIETCJgvn-Vn0i4b5ByP76bC3uBan4C-_EWZbdnvRhuScxq9MTjLjGQ84ZnLtRv0Ihk8pp20W2W_wDYgIqsmfn2ejPibWxc-tOxMSyGI7gWW4o1NsnQey06WW9LgKFwQW9AiWCDaoD5xPmaMR4HW_u5FiIaufSxFJKkuB4GH1CFJWOoXB-0rqoqVDa4UUoWfbJxCDSwIHu2wwIzhTrkHeFMHkUXV7IoAsFCNdhb-4y6ayA6E0Gkqnp_A"
            width={40}
            height={40}
            className="w-full h-full object-cover"
          />
        </div>
      </div>
    </header>
  );
}

