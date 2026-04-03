import {
  defineConfig,
  presetUno,
  presetAttributify,
  presetIcons
} from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      cdn: 'https://esm.sh/'
    })
  ],
  shortcuts: {
    'flex-center': 'flex items-center justify-center',
    'flex-between': 'flex items-center justify-between',
    'text-primary': 'text-blue-500',
    'text-success': 'text-green-500',
    'text-warning': 'text-orange-500',
    'text-error': 'text-red-500'
  },
  theme: {
    colors: {
      primary: '#2080f0',
      success: '#18a058',
      warning: '#f0a020',
      error: '#d03050'
    }
  }
})