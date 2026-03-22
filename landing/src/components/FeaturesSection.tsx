import { motion } from "framer-motion";

const features = [
  {
    icon: "✨",
    title: "Add perfumes in seconds",
    description: "Simply type a name — the bot recognizes thousands of fragrances instantly.",
  },
  {
    icon: "🎭",
    title: "Search by mood or notes",
    description: "Feeling cozy? Romantic? Let the bot match your mood to the perfect scent.",
  },
  {
    icon: "🤖",
    title: "AI fragrance suggestions",
    description: "Smart recommendations based on your taste, weather, and occasion.",
  },
  {
    icon: "📊",
    title: "Personal fragrance analytics",
    description: "Discover your scent profile — most-worn notes, seasonal patterns, and more.",
  },
  {
    icon: "🧴",
    title: "Minimal wardrobe overview",
    description: "A clean, beautiful view of everything you own — no clutter, no noise.",
  },
  {
    icon: "🌤",
    title: "Smart seasonal picks",
    description: "Get recommendations that match the season and temperature outside.",
  },
];

const FeaturesSection = () => (
  <section className="py-24 lg:py-32">
    <div className="container">
      <div className="text-center mb-16">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-sm font-medium text-primary mb-3"
        >
          Everything you need
        </motion.p>
        <motion.h2
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.05 }}
          className="font-display text-3xl sm:text-4xl text-foreground"
        >
          Your scent life, organized
        </motion.h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.4, delay: i * 0.06 }}
            className="group p-6 rounded-2xl bg-card border border-border soft-shadow hover:soft-shadow-lg transition-shadow duration-300"
          >
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-xl mb-5 group-hover:scale-105 transition-transform duration-200">
              {f.icon}
            </div>
            <h3 className="font-semibold text-foreground mb-2">{f.title}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);

export default FeaturesSection;
