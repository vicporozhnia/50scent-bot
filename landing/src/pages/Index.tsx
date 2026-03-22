import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import HowItWorks from "@/components/HowItWorks";
import EmotionalSection from "@/components/EmotionalSection";
import TestimonialsSection from "@/components/TestimonialsSection";
import FinalCTA from "@/components/FinalCTA";
import Footer from "@/components/Footer";

const Index = () => (
  <div className="min-h-screen bg-background text-foreground">
    <Navbar />
    <HeroSection />
    <FeaturesSection />
    <HowItWorks />
    <EmotionalSection />
    <TestimonialsSection />
    <FinalCTA />
    <Footer />
  </div>
);

export default Index;
