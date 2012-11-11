import imp

def load_config(file, namespace):
	loaded = imp.load_source("mouse", file)

	local_config = {}

	prefix = "%s/" % namespace
	global_prefix = "global/"

	# Grab all the configuration values for the given namespace, and any global
	# configuration values.
	for k, v in loaded.config.items():
		if k.startswith(prefix) and k != len(prefix):
			local_config[k[len(prefix):]] = v
		elif k.startswith(global_prefix) and k != len(global_prefix):
			local_config[k[len(global_prefix):]] = v
		else:
			print k, v

	return local_config