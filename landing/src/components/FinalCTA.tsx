import { motion } from "framer-motion";

const FinalCTA = () => (
  <section className="py-24 lg:py-32">
    <div className="container">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="relative max-w-2xl mx-auto text-center rounded-3xl bg-gradient-to-br from-primary/10 via-accent/10 to-primary/5 border border-border p-12 sm:p-16"
      >
        <h2 className="font-display text-3xl sm:text-4xl text-foreground mb-4">
          Ready to curate your{" "}
          <span className="italic text-primary">scent story</span>?
        </h2>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          Join hundreds of fragrance lovers who manage their perfume wardrobe with 50 scent. Free to start.
        </p>
        <motion.a
          href="https://t.me/fragrance_wardrobe_bot"
          target="_blank"
          rel="noopener noreferrer"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="inline-flex items-center justify-center gap-2 px-10 py-4 rounded-full bg-primary text-primary-foreground font-medium transition-all duration-200 hover:shadow-lg hover:shadow-primary/25"
        >
          Open in Telegram →
        </motion.a>
      </motion.div>
    </div>
  </section>
);

export default FinalCTA;
