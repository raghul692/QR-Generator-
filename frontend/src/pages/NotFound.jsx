import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BsCompass, BsHouseDoor } from 'react-icons/bs'

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card max-w-md w-full p-8 text-center"
      >
        <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <BsCompass className="text-white text-3xl" />
        </div>
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-2">404</h1>
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">Page Not Found</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
          The page you are looking for does not exist or has been moved.
        </p>
        <Link
          to="/"
          className="btn-primary inline-flex items-center justify-center gap-2 w-full py-2.5 text-sm font-medium"
        >
          <BsHouseDoor className="text-lg" />
          Back to Dashboard
        </Link>
      </motion.div>
    </div>
  )
}
