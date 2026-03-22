const Navbar = () => (
  <nav className="fixed top-0 left-0 right-0 z-50 glass-soft">
    <div className="container flex items-center justify-between h-16">
      <a href="/" className="font-display text-xl text-foreground">
        50 <span className="italic text-primary">scent</span>
      </a>
      <div className="hidden sm:flex items-center gap-8">
        <a href="#how-it-works" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
          How it works
        </a>
        <a
          href="https://t.me/fragrance_wardrobe_bot"
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium px-5 py-2 rounded-full bg-primary text-primary-foreground hover:shadow-md hover:shadow-primary/20 transition-all duration-200"
        >
          Open Bot
        </a>
      </div>
    </div>
  </nav>
);

export default Navbar;
