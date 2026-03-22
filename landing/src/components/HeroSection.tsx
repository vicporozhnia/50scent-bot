import { motion } from "framer-motion";
import PhoneMockup from "./PhoneMockup";

const HeroSection = () => (
  <section className="relative overflow-hidden">
    {/* Soft gradient orbs */}
    <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl -translate-y-1/2" />
    <div className="absolute top-20 right-1/4 w-80 h-80 bg-accent/30 rounded-full blur-3xl" />

    <div className="container relative z-10 pt-32 pb-20 lg:pt-40 lg:pb-32">
      <div className="flex flex-col lg:flex-row items-center gap-16 lg:gap-20">
        {/* Left — Copy */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
          className="flex-1 text-center lg:text-left max-w-xl"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-primary" />
            <span className="text-sm font-medium">Telegram Bot</span>
          </div>

          <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl text-foreground leading-[1.1] mb-6">
            Your personal{" "}
            <span className="italic text-primary">fragrance</span>{" "}
            wardrobe
          </h1>

          <p className="text-lg text-muted-foreground leading-relaxed mb-10 max-w-md mx-auto lg:mx-0">
            Track your perfumes. Choose your scent by mood.
            Fall in love with your collection again.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
            <motion.a
              href="https://t.me/fragrance_wardrobe_bot"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-full bg-primary text-primary-foreground font-medium text-sm transition-all duration-200 hover:shadow-lg hover:shadow-primary/25"
            >
              Open in Telegram
              <span>→</span>
            </motion.a>
            <a
              href="#how-it-works"
              className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-full border border-border text-foreground font-medium text-sm transition-colors duration-200 hover:bg-secondary"
            >
              How it works
            </a>
          </div>
        </motion.div>

        {/* Right — Phone */}
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
          className="flex-shrink-0"
        >
          <PhoneMockup />
        </motion.div>
      </div>
    </div>
  </section>
);

export default HeroSection;
