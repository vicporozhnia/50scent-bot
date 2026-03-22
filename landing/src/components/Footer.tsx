const Footer = () => (
  <footer className="border-t border-border py-12">
    <div className="container flex flex-col sm:flex-row items-center justify-between gap-4">
      <a href="/" className="font-display text-lg text-foreground">
        50 <span className="italic text-primary">scent</span>
      </a>
      <div className="flex items-center gap-6">
        <a
          href="https://t.me/fragrance_wardrobe_bot"
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Telegram
        </a>
      </div>
      <p className="text-xs text-muted-foreground">
        © {new Date().getFullYear()} 50 scent
      </p>
    </div>
  </footer>
);

export default Footer;
