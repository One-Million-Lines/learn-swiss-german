const Footer = () => (
  <footer className="border-t border-border bg-card/80 mt-auto">
    <div className="container mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-muted-foreground">
      <span>Free to use, built by <a
          href="https://linkedin.com/in/alexrada"
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium text-foreground hover:text-primary transition-colors"
        >
          Alex Rada
        </a> — learn Swiss German at your own pace 🇨🇭</span>
      <div className="flex items-center gap-4">
        <a href="/terms" className="hover:text-foreground transition-colors">Terms & Conditions</a>
        <a href="/privacy" className="hover:text-foreground transition-colors">Privacy Policy</a>
      </div>
    </div>
  </footer>
);

export default Footer;
