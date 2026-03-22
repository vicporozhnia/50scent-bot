import { motion } from "framer-motion";

const EmotionalSection = () => (
  <section className="py-24 lg:py-32">
    <div className="container">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl mx-auto text-center"
      >
        <div className="text-4xl mb-6">🤍</div>
        <h2 className="font-display text-3xl sm:text-4xl text-foreground mb-6 leading-snug">
          Fragrance is memory,{" "}
          <span className="italic text-primary">identity</span>,{" "}
          and daily ritual
        </h2>
        <p className="text-muted-foreground leading-relaxed text-lg">
          Every perfume tells a story. Every morning ritual of choosing a scent is an act of
          self-expression. 50 scent helps you honor that ritual — by giving your collection
          the care and attention it deserves. Simple, beautiful, and deeply personal.
        </p>
      </motion.div>
    </div>
  </section>
);

export default EmotionalSection;
